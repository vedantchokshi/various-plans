function updateVPToken(){
  var authResponse = gapi.auth2.getAuthInstance().currentUser.get().getAuthResponse();
  document.cookie = "vp-token=" + authResponse.id_token + "; expires=" + new Date(authResponse.expires_at).toGMTString() + "; path=/";
}

function redirectWithFreshToken(path) {
  updateVPToken();
  window.location = path;
}

var localSession = {
    //The events and routes that the client browser is tracking
    events: [],
    routes: [],
    //List of markers shown on map for search results
    searchmarkers: [],
    sidebarMenuIndex: 0,
    //The plan object representing this plan session
    plan: {id: 0},
    /*Returns an integer indicating the phase of this plan session
     * 0: Voting on /Adding Events
     * 1: Voting on /Adding Routes
     * 2: Displaying final Route
     */
    lastCheckedPhase: 1,
    getPhase: function() {
        var currTime = Math.floor((new Date()).getTime() / 1000);
        if(currTime > this.plan.routeVoteCloseTime)
            return 3;
        if(currTime > this.plan.eventVoteCloseTime)
            return 2;
        return 1;
    },
    timeToPhaseEnd: function() {
        var currTime = Math.floor((new Date()).getTime() / 1000);
        if(currTime <= this.plan.eventVoteCloseTime)
            return this.plan.eventVoteCloseTime - currTime;
        if(currTime <= this.plan.routeVoteCloseTime)
            return this.plan.routeVoteCloseTime - currTime;
        return -1;
    },
    enterPhase2: function() {
        this.lastCheckedPhase = 2;
        console.log("Entered Phase 2");
        //Update UI
        $("#sidebar-menu").find(".menu-heading").html("Decide Routes"); //Change Heading
        $("#sidebar-menu").find(".menu-content").empty(); //Clear voting controls for events
        $("#map-search").css("display", "none"); //Search no longer needed
        $("#modalPlace").modal("hide"); //Hide place modal if open
        removeMarkersFromMap(this.searchmarkers); //Clear any search markers from map
        localSession.searchmarkers = [];

        $("<div>", { "id" : "route-list" }).appendTo($("#sidebar-menu").find(".menu-content"));

        //Reset Available events
        this.events.forEach(function(event) {
            event.marker.setMap(null);
        });
        this.events = [];

        //Add new events to map, but not sidebar
        updateEvents(false, true).then(function() {
            fitEventsOnMap(localSession.events);

            $("<button>", {"id": "add-route-button", "class": "btn btn-default", "type": "button", text: "Add Route"})
                .appendTo($("#sidebar-menu").find(".menu-content"))
                .click(function() {
                    $("#modalRoute").modal("show");
                });
        }, function(error_obj) {
          //Api Load Events Error
        });
        //TODO: what if no one has submitted anything?
    },
    enterPhase3: function() {
        this.lastCheckedPhase = 3;
        console.log("Entered Phase 3");
        //Clear UI
        $("#map-search").css("display", "none"); //Search no longer needed
        $("#modalPlace").modal("hide"); //Hide place modal if open
        $("#modalRoute").modal("hide"); //Hide route modal if open
        removeMarkersFromMap(this.searchmarkers); //Clear any search markers from map
        localSession.searchmarkers = [];

        //Reset Available events
        this.events.forEach(function(event) {
            event.marker.setMap(null);
        });
        this.events = [];

        //Reset Available routes
        this.routes.forEach(function(route) {
            route.directionsRenderer.setMap(null);
        });
        this.routes = [];

        //Add new events to map, but not sidebar
        //In phase 3 /api/plan/<id>/events returns only the events in the winning route
        updateEvents(false, true).then(function() {
            fitEventsOnMap(localSession.events);

            updateRoutes(false, true).then(function(routes) {
                fitEventsOnMap(localSession.events);
                //In phase 3, /api/plan/<id>/routes returns singleton containing winning routes
                var route = routes[0];
                $("#sidebar-menu").find(".menu-heading").html("Final Route");
                $("#sidebar-menu").find(".menu-content").empty();
                $("#sidebar-menu").find(".menu-content")
                    .append($("<span>", {text: "Name: " + route.name})).append("<br>")
                    .append($("<span>", {text: "Description: <Add desc pls>"})).append("<br>")
                    .append($("<span>", {text: "Current Votes: " + String(route.votes)})).append("<br>")
                    .append($("<span>", {text: "Stops"})).append("<br>");

                //Add each event to info page
                route.getIncludedEvents().forEach(function(route) {
                    route.displayUI($("#sidebar-menu").find(".menu-content"), false);
                });
            }, function(error_obj) {
              //Api Load Routes Error
            });
        }, function(error_obj) {
            //Api Load Events Error
        });
        //TODO: what if no one has submitted anything?
    },

    initialise: function() {
        //Initialise GMaps API
        this.initGMaps();
        //Initialise Session Variables
        this.initSessionVars();
        //Initialise UI
        this.initUI();
        //Init Polling
        setInterval(pollServer, 1000);
    },
    initSessionVars: function(){
        //Poll server for initial plan information
        this.plan = _apiLoad.plan;
        this.lastCheckedPhase = this.plan.phase;

        switch(this.getPhase()) {
            case 1:
                //Add new events and reposition map
                updateEvents(true, true).then(function() {
                    fitEventsOnMap(localSession.events);
                }, function(error_obj) {

                });
                break;
            case 2:
                this.enterPhase2();
                break;
            case 3:
                this.enterPhase3();
                break;
        }
    },
    initGMaps: function() {
        var map = this.map = new google.maps.Map($("#map")[0], {
            zoom: 8,
            center: {lat: -34.397, lng: 150.644}
        });
        var placesService = this.placesService = new google.maps.places.PlacesService(map);
        this.directionsService = new google.maps.DirectionsService();

        var input = $("#map-search")[0];
        var searchBox = new google.maps.places.SearchBox(input);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

        // Bias the SearchBox results towards current map's viewport.
        map.addListener('bounds_changed', function() {
            searchBox.setBounds(map.getBounds());
        });

        // Listen for the event fired when the user selects a prediction and retrieve
        // more details for that place.
        searchBox.addListener('places_changed', function() {
            var places = searchBox.getPlaces();

            if (places.length == 0) {
                return;
            }

            // Clear out the old markers.
            localSession.searchmarkers.forEach(function(marker) {
                marker.setMap(null);
            });
            localSession.searchmarkers = [];

            // For each place, get the icon, name and location.
            var bounds = new google.maps.LatLngBounds();
            places.forEach(function(place) {
                if(isPlaceAdded(place.place_id)){
                    //Place already added so skip to next iteration
                    return true;
                }

                if (!place.geometry) {
                    console.log("Returned place contains no geometry");
                    return;
                }
                var icon = {
                    url: place.icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                };

                // Create a marker for each place.
                var marker = new google.maps.Marker({
                    map: map,
                    icon: icon,
                    title: place.name,
                    place: {
                        location: place.geometry.location,
                        placeId: place.place_id
                    }
                });

                marker.addListener('mouseover', function() {
                    if(localSession.getPhase() === 1) {
                        var markerIco = this.getIcon();
                        markerIco.scaledSize = new google.maps.Size(41, 41);
                        markerIco.anchor = new google.maps.Point(markerIco.anchor.x+8,markerIco.anchor.y+8);
                        marker.setIcon(markerIco);
                    }
                });

                marker.addListener('mouseout', function() {
                    if(localSession.getPhase() === 1) {
                        var markerIco = this.getIcon();
                        markerIco.scaledSize = new google.maps.Size(25, 25);
                        markerIco.anchor = new google.maps.Point(markerIco.anchor.x-8, markerIco.anchor.y-8);
                        marker.setIcon(markerIco);
                    }
                });

                marker.addListener('click', function() {
                    if(localSession.getPhase() === 1) {
                        placesService.getDetails({placeId: this.getPlace().placeId}, function(place, status) {
                            if (status === google.maps.places.PlacesServiceStatus.OK) {
                                $("#modalPlace").data("place", place).modal('show');
                            }
                        });
                    }
                });

                localSession.searchmarkers.push(marker);

                if (place.geometry.viewport) {
                    // Only geocodes have viewport.
                    bounds.union(place.geometry.viewport);
                } else {
                    bounds.extend(place.geometry.location);
                }
            });
            map.fitBounds(bounds);
        });
    },
    initUI: function() {
        $("#modalPlace").on('show.bs.modal', function (event) {
            var modal = $(this);
            modal.find(".error-message").hide();
            modal.find("#event-name").val("");
            var place = modal.data("place");
            modal.find("#place-details").html("Suggest " + place.name + " as an event?");
            modal.find("#add-place").off("click").click(function() {
                var inputName = $("#modalPlace").find("#event-name").val();
                if(inputName.length === 0) {
                    $("#modalPlace").find(".error-message").html("Please enter a name.");
                    $("#modalPlace").find(".error-message").hide().fadeIn();
                } else if(inputName.length >= 100) {
                    $("#modalPlace").find(".error-message").html("Name too long.");
                    $("#modalPlace").find(".error-message").hide().fadeIn();
                  } else {
                    //Remove the markers for the other search results
                    removeMarkersFromMap(localSession.searchmarkers);
                    localSession.searchmarkers = [];
                    //Notify server of event creation
                    api.event.create(inputName, localSession.plan.id, place.place_id).then(function(response) {
                      //Create event from server response
                      Event.EventFactory(response, place).then(function(event) {
                        //Track event in session
                        localSession.events[event.id] = event;
                        //Render event
                        event.display();
                        //Reposition map
                        fitEventsOnMap(localSession.events);
                        modal.modal('hide');
                      }, function() {
                        //TODO: Better Error mesage
                        alert("Couldn't add event.");
                      });
                    },
                    function(error_obj) {
                      console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
                    });
                  }
            });
        });

        $(".route-sortable").sortable({connectWith: ".route-sortable", scroll: false}).css("cursor", "pointer");

        $("#modalRoute").on('show.bs.modal', function (event) {
            $(this).find(".error-message").hide();
            $(this).find("#route-name").val("");
            //Clear lists
            $("#modalRoute").find(".route-sortable").empty();
            //Repopulate list with available events
            localSession.events.forEach(function(event) {
                $("<li>", { text: event.name, "class": "ui-state-default" }).data("event-id", event.id).appendTo($("#modalRoute").find(".available-event-list"));
            });
        });

        $("#modalRoute").find("#add-route").click(function() {
            var inputName = $("#modalRoute").find("#route-name").val();

            var routeEvents = $("#modalRoute").find(".route-event-list").find("li");
            var eventList = [];
            for(var i = 0; i < routeEvents.length; i++) {
                eventList.push($(routeEvents[i]).data("event-id"));
            }

            if(inputName.length === 0) {
                $("#modalRoute").find(".error-message").html("Please enter a name.");
                $("#modalRoute").find(".error-message").hide().fadeIn();
            } else if(inputName.length >= 100) {
                $("#modalRoute").find(".error-message").html("Name too long.");
                $("#modalRoute").find(".error-message").hide().fadeIn();
            } else if(eventList.length === 0){
                $("#modalRoute").find(".error-message").html("Please add events to the route.");
                $("#modalRoute").find(".error-message").hide().fadeIn();
              } else {
                api.route.create($("#modalRoute").find("#route-name").val(), localSession.plan.id, eventList).then(function(response) {

                  //Prevent polling duplicating the object
                  localSession.routes[response.id] = "pending";

                  //Create event from server response
                  Route.RouteFactory(response).then(function(route) {
                    //Track event in session
                    localSession.routes[route.id] = route;
                    route.display();
                    //TODO: Reposition map
                    $("#modalRoute").modal('hide');
                  });
                }, function(error_obj) {
                  console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
                });
              }
        });
    }
};

function initMap() {
    //Initialise the local session
    localSession.initialise();
}

//Reposition map to show all given events
function fitEventsOnMap(eventList) {
    //Show all markers on map
    var bounds = new google.maps.LatLngBounds();
    eventList.forEach(function(event) {
        //Viewport looks better when the map is fitted to single place with a view port
        //When fitted to multiple points, location looks better
        if (event.place.geometry.viewport && Object.keys(eventList).length === 1) {
            // Only geocodes have viewport.
            bounds.union(event.place.geometry.viewport);
        } else {
            bounds.extend(event.place.geometry.location);
        }
    });
    localSession.map.fitBounds(bounds);
}

function removeMarkersFromMap(markers) {
    //Remove markers from map
    markers.forEach(function(marker) {
        marker.setMap(null);
    });
}

function addMarkerToMap(place) {
    var icon = {
        url: '../../static/assets/img/Screen Shot 2017-12-19 at 20.13.38.png',
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 20),
        scaledSize: new google.maps.Size(25, 25)
    };

    // Create a marker for each place.
    return new google.maps.Marker({
        map: localSession.map,
        icon: icon,
        title: place.name,
        animation: google.maps.Animation.DROP,
        place: {
            location: place.geometry.location,
            placeId: place.place_id
        }
    });
}

function isPlaceAdded(placeId) {
    var placeAdded = false;
    localSession.events.forEach(function(event) {
        if(event.place.place_id === placeId) {
            placeAdded = true;
            return false; //Break from forEach loop
        }
    });
    return placeAdded;
}

function displayEventInfo(event) {
    localSession.sidebarMenuIndex++;
    var submenu = "#sidebar-sub" + localSession.sidebarMenuIndex;
    $(submenu).find(".menu-heading").html("Event Info");
    $(submenu).find(".menu-content").empty();
    $(submenu).find(".menu-content")
        .append($("<span>", {text: "Name: " + event.name})).append("<br>")
        .append($("<span>", {text: "Description: <Add desc pls>"})).append("<br>")
        .append($("<span>", {text: "Current Votes: " + String(event.votes)})).append("<br>")
        .append($("<span>", {text: "Venue: " + event.place.name})).append("<br>")
        .append($("<span>", {text: "Address: " + event.place.formatted_address})).append("<br>");

    //Add photo gallery if there are photos
    if(event.place.photos !== undefined && event.place.photos.length > 0) {
        new PhotoGallery(event.place.photos, Math.floor($(submenu).width() * 0.8)).render($(submenu).find(".menu-content"));
    }

    $(submenu).find(".prev-menu-button").off("click").click(function() {
        localSession.sidebarMenuIndex--;
        event.marker.setAnimation(null); //Stop Bouncing
        openMenu(localSession.sidebarMenuIndex);
        fitEventsOnMap(localSession.events);
    });
    openMenu(localSession.sidebarMenuIndex);
}

function displayRouteInfo(route) {
    localSession.sidebarMenuIndex++;
    var submenu = "#sidebar-sub" + localSession.sidebarMenuIndex;
    $(submenu).find(".menu-heading").html("Route Info");
    $(submenu).find(".menu-content").empty();
    $(submenu).find(".menu-content")
        .append($("<span>", {text: "Name: " + route.name})).append("<br>")
        .append($("<span>", {text: "Description: <Add desc pls>"})).append("<br>")
        .append($("<span>", {text: "Current Votes: " + String(route.votes)})).append("<br>")
        .append($("<span>", {text: "Stops"})).append("<br>");

    //Add each event to info page
    route.getIncludedEvents().forEach(function(route) {
        route.displayUI($(submenu).find(".menu-content"), false);
    });

    //Give back button functionality
    $(submenu).find(".prev-menu-button").off("click").click(function() {
        localSession.sidebarMenuIndex--;
        openMenu(localSession.sidebarMenuIndex);
        //Make all route lines and markers visible again
        localSession.routes.forEach(function(route) {
            route.setVisibleOnMap(true);
        });
        localSession.events.forEach(function(event) {
            event.setVisibleOnMap(true);
        });
        fitEventsOnMap(localSession.events);
    });
    openMenu(localSession.sidebarMenuIndex);
}

//Moves menus to given level - 0 is base menu
function openMenu(level) {
    $(".sidebar-menu").animate({ left: "-" + ($(".sidebar-menu").width() * level) });
}

//POLLING
function millisToReadable(millis){
    var days, hours, mins, secs, readable;
    secs = Math.floor(millis / 1000);
    mins = Math.floor(secs / 60);
    secs = secs % 60;
    hours = Math.floor(mins / 60);
    mins = mins % 60;
    days = Math.floor(hours / 24);
    hours = hours % 24;
    readable = "";
    readable += days > 0 ? days + "d " : "";
    readable += hours > 0 ? hours + "h " : "";
    readable += mins > 0 ? mins + "m " : "";
    return readable + secs + "s";
}

function pollServer() {
    //console.log("Polling Server...");
    //Get current phase that session is in
    var phase = localSession.getPhase();
    //console.log("Currently in phase " + phase);

    //Update countdown timer
    var timeRemaining = localSession.timeToPhaseEnd();
    if(timeRemaining > -1) {
        $("#countdown-timer").html("Voting ends in " + millisToReadable(timeRemaining*1000));
    } else {
        $("#countdown-timer").html("");
    }

    if(phase == 1) {
        //Event voting phase, update events
        updateEvents(true, true).then(null, function(error_obj) {
          console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
        });
    } else if(phase == 2) {
        //Route voting phase
        if(localSession.lastCheckedPhase != 2) {
            localSession.enterPhase2();
        }
        //Update Routes
        updateRoutes(true, true).then(null, function(error_obj) {
          console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
        });
    } else if (phase == 3) {
        //Final route phase
        if(localSession.lastCheckedPhase != 3) {
            localSession.enterPhase3();
        }
        //additional updates go here
    }
}

//Update the events tracked locally by polling backend API
//Optionally display new events in map and sidebar
function updateEvents(displayNewEvents, displayOnMap) {
  return new Promise(function(updateEventsSuccess, updateEventsError) {
    api.plan.getEvents(localSession.plan.id).then(function(eventsResponse){
      var serverEvents = eventsResponse.results;
      var eventPromises = [];
      serverEvents.forEach(function(e) {
        var localEvent = localSession.events[e.id];
        //If event is new to client
        if(localEvent === undefined) {
          //Lock array element to prevent multiple async calls to this function creating duplicate objects
          localSession.events[e.id] = "pending";
          //Create new object
          var promise = Event.EventFactory(e, null);
          eventPromises.push(promise);
          promise.then(function(event) {
            //Add to event list
            localSession.events[event.id] = event;
            if(displayNewEvents) {
              //Display event
              event.displayUI($("#sidebar-menu .menu-content"), true);
            }
            if(displayOnMap) {
              //Display event
              event.displayOnMap();
            }
          });
        } else if(localEvent === "pending") {
          //Do nothing, it is being handled by other call
        } else {
          //Otherwise update event object as it exists
          Object.assign(localEvent, e);
          //Refresh UI
          localEvent.refreshUI();
        }
      });
      Promise.all(eventPromises).then(updateEventsSuccess);
    },
    function(error_obj){
      updateEventsError(error_obj);
    });
  });
}

//Update the routes tracked locally by polling backend API
//Optionally display new routes in map and sidebar
function updateRoutes(displayNewRoutes, displayOnMap) {
  return new Promise(function(updateRoutesSuccess, updateRoutesError) {
    api.plan.getRoutes(localSession.plan.id).then(function(routesResponse){
      var serverRoutes = routesResponse.results;
      var routePromises = [];
      serverRoutes.forEach(function(r) {
        var localRoute = localSession.routes[r.id];
        //If route is new to client
        if(localRoute === undefined) {
          //Lock array element to prevent multiple async calls to this function creating duplicate objects
          localSession.routes[r.id] = "pending";
          //Create new object
          var promise = Route.RouteFactory(r);
          routePromises.push(promise);
          promise.then(function(route) {
            //Add to event list
            localSession.routes[route.id] = route;
            if(displayNewRoutes) {
              //Display event
              route.displayUI($("#sidebar-menu #route-list"), true);
            }
            if(displayOnMap) {
              //Display event
              route.displayOnMap();
            }
          });
        } else if(localRoute === "pending") {
          //Do nothing, it is being handled by other call
        } else {
          //Otherwise update event object as it exists
          Object.assign(localRoute, r);
          //Refresh UI
          localRoute.refreshUI();
        }
      });
      Promise.all(routePromises).then(updateRoutesSuccess);
    },
    function(error_obj){
      updateRoutesError(error_obj);
    });
  });
}
