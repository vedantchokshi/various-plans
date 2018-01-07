class VoteEntry {
  constructor(name, value) {
    this.entry = $("<div>", { "class": "vote-entry"});
    this.voteControlContainer = $("<div>", {"class" : "vote-control-wrapper"}).appendTo(this.entry);
    this.voteup = $("<div>", {"class" : "vote-up"}).appendTo(this.voteControlContainer);
    this.votecount = $("<span>", { "class" : "vote-entry-count",
    text: String(value)}).appendTo(this.voteControlContainer);
    this.votedown = $("<div>", {"class" : "vote-down"}).appendTo(this.voteControlContainer);
    this.labelWrapper = $("<div>", {"class" : "vote-label-wrapper"}).appendTo(this.entry);
    this.label = $("<span>", { "class" : "vote-entry-label",
    text: name}).appendTo(this.labelWrapper);
  }

  update(value, state) {
    this.votecount.html(String(value));
    switch(state) {
      case 1:
          this.voteup.addClass("selected");
          this.votedown.removeClass("selected");
          break;
      case 0:
          this.voteup.removeClass("selected");
          this.votedown.removeClass("selected");
          break;
      case -1:
          this.voteup.removeClass("selected");
          this.votedown.addClass("selected");
          break;
    }
  }

  highlight(on) {
    if(on) {
      this.entry.addClass("highlight");
    } else {
      this.entry.removeClass("highlight");
    }
  }
}

class Votable {
    constructor(apiJsonResponse) {
        //Assign values from object returned from API
        Object.assign(this, apiJsonResponse);

        //Create HTML DOM of entry
        this.dom = new VoteEntry(this.name, this.votes);
    }

  upvote() {
    var votePromise;
    if(this.userVoteState === 1) {
      //Remove upvote
      votePromise = Votable.callApi(this.constructor.name).resetvote(this.id);
    } else {
      votePromise = Votable.callApi(this.constructor.name).upvote(this.id);
    }
    var self = this;
    votePromise.then(function(result) {
      self.votes = result.votes;
      self.userVoteState = result.userVoteState;
      self.timestamp = result.timestamp;
      self.refreshUI();
    }, function(error_obj) {
      console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
    });
  }

  downvote() {
    var votePromise;
    if(this.userVoteState === -1) {
      //Remove downvote
      votePromise = Votable.callApi(this.constructor.name).resetvote(this.id);
    } else {
      votePromise = Votable.callApi(this.constructor.name).downvote(this.id);
    }
    var self = this;
    votePromise.then(function(result) {
      self.votes = result.votes;
      self.userVoteState = result.userVoteState;
      self.timestamp = result.timestamp;
      self.refreshUI();
    }, function(error_obj) {
      console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
    });
  }

  select() {}

  mouseover() { this.dom.highlight(true); }
  mouseout() { this.dom.highlight(false); }

  //Adds HTML Elements to sidebar for this route or event
  displayUI(container, showVoteControls) {
      //Event Listeners
      var self = this; //Use variable as this refers to HTML element in the listener context
      this.dom.voteup.off("click").click(function() { self.upvote(); });
      this.dom.votedown.off("click").click(function() { self.downvote(); });

      this.dom.entry.off("mouseover").mouseover(function() { self.mouseover(); });
      this.dom.entry.off("mouseout").mouseout(function() { self.mouseout(); });

      //Return false to prevent vote buttons from triggering this click
      this.dom.entry.off("click").click(function() { self.select(); })
          .find(".vote-up, .vote-down").click(function() { return false; });

      //Whether to display the vote controls (UI is displayed for route info submenu aswell)
      this.dom.voteControlContainer.css("display", showVoteControls ? "inline-block" : "none");
      //Add entry to containing element
      container.append(this.dom.entry);
  }

  //Hides or shows HTML Elements in sidebar for this route or event
  setUIVisible(visible) {
      this.dom.entry.css("display", visible ? "block" : "hidden");
  }

  //Updates the info displayed in the HTML elements
  refreshUI() {
    this.dom.update(this.votes, this.userVoteState);
  }

  static callApi(className) {
      if(Votable.apiCalls[className] === undefined)
          console.error("No api calls defined in Votabe for subclass, " + className);
      else
          return Votable.apiCalls[className];
  }
}

Votable.apiCalls = {};

class Event extends Votable {
  //Creates Event which potentially needs to happen asynchronously
  //Returns promise that is resolved when Event is created
  static EventFactory(apiJSON, place) {
    return new Promise(function(resolve, reject) {
      if(place === undefined || place === null) {
        var f = function() {
          //Get place from Google API
          localSession.placesService.getDetails({placeId: apiJSON.locationid}, function(_place, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
              resolve(new Event(apiJSON, _place));
            } else if (status === google.maps.places.PlacesServiceStatus.OVER_QUERY_LIMIT) {
              setInterval(f, 20);
            } else {
              reject(status);
            }
          });
        };
        f();
      } else {
        resolve(new Event(apiJSON, place));
      }
    });
  }

  constructor(apiJSON, place) {
    //Assign values from object returned from API
    super(apiJSON);
    this.place = place;
    this.marker = null;
  }

  select() {
    //Reposition map if marker is not in view
    if(!localSession.map.getBounds().contains(this.place.geometry.location))
    fitEventsOnMap([this]);

    if(this.marker !== undefined)
        this.marker.setAnimation(google.maps.Animation.BOUNCE);
    //Show info in the menu
    displayEventInfo(this);
  }

  mouseover() {
    super.mouseover();
    this.highlightMarker(true);
  }

  mouseout() {
    super.mouseout();
    this.highlightMarker(false);
  }

  //Adds the HTML elements to sidebar and marker to the map
  display() {
      super.displayUI($("#sidebar-menu .menu-content"), true);
      //Add Marker to Map
      this.displayOnMap();
  }

  //Adds the marker to the map
  displayOnMap() {
      //Add Marker to Map
      this.marker = addMarkerToMap(this.place);
      var self = this;
      this.marker.addListener('mouseover', function() {
          self.highlightMarker(true);
          self.dom.highlight(true);
          localSession.routes.forEach(function(route) {
              if(route.eventidList.includes(self.id))
                  route.dom.highlight(true);
          });
      });

      this.marker.addListener('mouseout', function() {
          self.highlightMarker(false);
          self.dom.highlight(false);
          localSession.routes.forEach(function(route) {
              if(route.eventidList.includes(self.id))
                  route.dom.highlight(false);
          });
      });
  }

  //Shows or hides the HTML elements in sidebar and marker on map
  setVisible(visible) {
      super.setUIVisible(visible);
      this.setVisibleOnMap(visible);
  }

  //Shows or hides marker on map
  setVisibleOnMap(visible) {
      this.marker.setMap(visible ? localSession.map : null);
  }

  highlightMarker(on) {
      var markerIco = this.marker.getIcon();
      if(on) {
          markerIco.scaledSize = new google.maps.Size(31, 31);
          markerIco.anchor = new google.maps.Point(markerIco.anchor.x+3,markerIco.anchor.y+3);
      } else {
          markerIco.scaledSize = new google.maps.Size(25, 25);
          markerIco.anchor = new google.maps.Point(markerIco.anchor.x-3, markerIco.anchor.y-3);
      }
      this.marker.setIcon(markerIco);
  }
}
Votable.apiCalls.Event = api.event;

class Route extends Votable {
  //Creates Route objects from json response from backend API
  static RouteFactory(apiJSON) {
    var eventIdArr = apiJSON.eventidList;
    var request = { travelMode: google.maps.TravelMode.WALKING };
    request.origin = localSession.events[eventIdArr[0]].place.geometry.location;
    request.destination = localSession.events[eventIdArr[eventIdArr.length - 1]].place.geometry.location;

    if(eventIdArr.length > 2) {
      request.waypoints = [];
      for(var i = 1; i < eventIdArr.length - 1; i++) {
        var waypointEvent = localSession.events[eventIdArr[i]];
        request.waypoints.push({location: waypointEvent.place.geometry.location});
      }
    }

    return new Promise(function(resolve, reject) {
      var f = function(){
        localSession.directionsService.route(request, function(direction, status) {
          if (status === google.maps.DirectionsStatus.OK) {
            resolve(new Route(apiJSON, direction));
          } else if (status === google.maps.DirectionsStatus.OVER_QUERY_LIMIT) {
            setTimeout(f, 20);
          } else {
            reject(status);
          }
        });
      };
      f();
    });
  }

  constructor(apiJSON, direction) {
    super(apiJSON);
    //DirectionsResult object from GMaps API
    this.direction = direction;
    this.lineRenderOptions = { strokeColor: "#208DE6", strokeWeight: 6, strokeOpacity: 0.6 };
    this.directionsRenderer = new google.maps.DirectionsRenderer({ map: localSession.map, suppressMarkers: true, polylineOptions : this.lineRenderOptions, preserveViewport: true });
  }

  //Applies the specified options to the polylineOptions and re-renders line
  editLineOptions(options) {
      Object.assign(this.lineRenderOptions, options);
      this.directionsRenderer.setDirections(this.direction);
  }

  select() {
    var eventsInRoute = [];
    //Gather events in route, making the rest invisible
    var eventidList = this.eventidList;
    localSession.events.forEach(function(event) {
        if(eventidList.includes(event.id))
            eventsInRoute.push(event);
        else
            event.setVisibleOnMap(false);
    });
    fitEventsOnMap(eventsInRoute);
    //Remove other lines
    var thisId = this.id;
    localSession.routes.forEach(function(route) {
        if(route.id !== thisId)
            route.setVisibleOnMap(false);
    });
    //Show info in the menu
    displayRouteInfo(this);
  }

  mouseover() {
      super.mouseover();
      //Fade out other lines
      var thisId = this.id;
      localSession.routes.forEach(function(route) {
          if(route.id !== thisId)
            route.editLineOptions({ strokeOpacity: 0 });
      });
      //Enlarge included event markers
      this.eventidList.forEach(function(eventId) {
          localSession.events[eventId].highlightMarker(true);
      });
  }

  mouseout() {
      super.mouseout();
      //Reset line opacities
      localSession.routes.forEach(function(route) {
          route.editLineOptions({ strokeOpacity: 0.6 });
      });
      //Reset included event markers
      this.eventidList.forEach(function(eventId) {
          localSession.events[eventId].highlightMarker(false);
      });
  }

  //Adds the HTML elements to sidebar and route line to the map
  display() {
      super.displayUI($("#sidebar-menu #route-list"), true);
      //Render Route on Map
      this.displayOnMap();
  }

  //Adds the route line to the map
  displayOnMap(){
      //Render Route on Map
      this.directionsRenderer.setDirections(this.direction);
  }

  //Shows or hides the HTML elements in sidebar and route line on map
  setVisible(visible) {
      super.setUIVisible(visible);
      //Render Route on Map
      this.setVisibleOnMap(visible);
  }

  //Shows or hides route line on map
  setVisibleOnMap(visible) {
      //Render Route on Map
      this.editLineOptions({ visible: visible });
  }

  getIncludedEvents() {
      var includedEventsArr = [];
      this.eventidList.forEach(function(eventId) {
          includedEventsArr.push(localSession.events[eventId]);
      });
      return includedEventsArr;
  }
}
Votable.apiCalls.Route = api.route;
