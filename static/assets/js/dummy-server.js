var currTimeForDummy = (new Date()).getTime();
var dummyServer = {
  plans: [{
    id: 0,
    name: "Test Plan",
    eventVoteCloseTime: currTimeForDummy-1000, //1 hour from start
    routeVoteCloseTime: currTimeForDummy+100000000, //2 hours from start
    creationTime: currTimeForDummy
  }],
  events: [{
    id: 0,
    planid: 0,
    name: "Southampton",
    locationid: "ChIJCSkVvleJc0gR8HHaTGpajKc",
    votes: 0
  },{
    id: 1,
    planid: 0,
    name: "Oceana",
    locationid: "ChIJ-YIFG7l2dEgRRUQ6kcgvXYY",
    votes: 0
  },{
    id: 2,
    planid: 0,
    name: "Premier Express",
    locationid: "ChIJi4BkO7t2dEgRR3aPzmjHPV0",
    votes: 0
  },{
    id: 3,
    planid: 0,
    name: "Tesco Express",
    locationid: "ChIJ3aG9YbZ2dEgRAAS4OrXY0lM",
    votes: 0
  },{
    id: 4,
    planid: 0,
    name: "KFC",
    locationid: "ChIJk-Bslid0dEgRJcmbtCJW3f0",
    votes: 0
  }],
  routes: [
    {
      id: 0,
      planid: 0,
      name: "Test Route",
      eventidList: [0,2,4],
      votes: 0
    }
  ],

  //Tracks user's vote states
  userEventVotes: [],
  userRouteVotes: [],


  getUserVoteState: function(eventrouteid, userid, forEvent) {
    var userVotes = forEvent ? this.userEventVotes : this.userRouteVotes;
    if(userVotes[userid] === undefined) {
      userVotes[userid] = [];
    }
    if(userVotes[userid][eventrouteid] === undefined) {
      userVotes[userid][eventrouteid] = 0;
    }
    return userVotes[userid][eventrouteid];
  },

  ////////////////////////PLANS///////////////////////

  /*Example plan object structure
  Whats stored in plans[]
  var egplan = {
  id: 0,
  name: "plan",
  eventVoteCloseTime: 0,
  routeVoteCloseTime: 0,
  creationTime: 0
};*/

planGET: function(id) {
  return "<!DOCTYPE html> <html>  <head>     <meta charset=\"utf-8\">     <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">     <title>Merged</title>     <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css\">     <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap-theme.min.css\">     <link rel=\"stylesheet\" href=\"static/assets/css/jquery-ui.min.css\">     <link rel=\"stylesheet\" href=\"static/assets/css/jquery-ui.structure.min.css\">     <link rel=\"stylesheet\" href=\"static/assets/css/jquery-ui.theme.min.css\">     <link rel=\"stylesheet\" href=\"static/assets/css/styles.css\"> </head>  <body class=\"backgroundFeatures\">     <div class=\"page-header\" id=\"header\">         <h1 id=\"navBar\"><img src=\"static/assets/img/Screen Shot 2017-12-19 at 20.13.38.png\" style=\"width:50px;border-radius:10px;margin-top:7px;margin-left:4px;\"><small style=\"color:rgb(255,255,255);\"> Various Plans</small><span id=\"countdown-timer\"> </span></h1>     </div>     <div>         <div class=\"container-fluid\">             <div class=\"row\">                 <div class=\"col-md-6 col-xs-8\" id=\"col1\"><input type=\"text\" placeholder=\"Search Location\" id=\"map-search\">                     <div id=\"map\"></div>                 </div>                 <div class=\"col-md-6\" id=\"col2\">                     <div id=\"sidebar-menu\" class=\"sidebar-menu\">                         <h1 class=\"menu-heading\">Decide Places </h1>                         <hr class=\"menu-rule\">                         <div id=\"places-list\" class=\"menu-content\"></div>                     </div>                     <div id=\"sidebar-sub1\" class=\"sidebar-menu\">                         <div class=\"prev-menu-button\"></div>                         <h1 class=\"menu-heading\"> </h1>                         <hr class=\"menu-rule\">                         <div class=\"menu-content\"></div>                     </div>                     <div id=\"sidebar-sub2\" class=\"sidebar-menu\">                         <div class=\"prev-menu-button\"></div>                         <h1 class=\"menu-heading\"> </h1>                         <hr class=\"menu-rule\">                         <div class=\"menu-content\"></div>                     </div>                 </div>             </div>         </div>     </div>     <div class=\"modal fade\" role=\"dialog\" tabindex=\"-1\" id=\"modalPlace\">         <div class=\"modal-dialog\" role=\"document\">             <div class=\"modal-content\">                 <div class=\"modal-header\" style=\"background-color:rgb(151,194,86);\"><button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button>                     <h4 class=\"modal-title\" style=\"color:rgb(255,255,255);\">Add New Place </h4>                 </div>                 <div class=\"modal-body\"><span id=\"place-details\"> </span>                     <div class=\"row\">                         <div class=\"col-md-12\"><label>Event Name</label><input type=\"text\" id=\"event-name\"><span class=\"error-message\"> </span></div>                     </div>                 </div>                 <div class=\"modal-footer\"><button class=\"btn btn-default\" type=\"button\" data-dismiss=\"modal\">Close</button><button class=\"btn btn-primary\" type=\"button\" id=\"add-place\">Add </button></div>             </div>         </div>     </div>     <div class=\"modal fade\" role=\"dialog\" tabindex=\"-1\" id=\"modalRoute\">         <div class=\"modal-dialog\" role=\"document\">             <div class=\"modal-content\">                 <div class=\"modal-header\" style=\"background-color:rgb(151,194,86);\"><button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button>                     <h4 class=\"modal-title\" style=\"color:rgb(255,255,255);font-size:27px;\">Create Route</h4>                 </div>                 <div class=\"modal-body\">                     <div class=\"row\">                         <div class=\"col-md-12\"><label>Route Name</label><input type=\"text\" id=\"route-name\"><span class=\"error-message\"> </span></div>                     </div>                     <div class=\"row\">                         <div class=\"col-md-12\" style=\"width:50%;\">                             <h1 style=\"font-size:24px;\">Events </h1>                             <ul class=\"route-sortable available-event-list\"></ul>                         </div>                         <div class=\"col-md-12\" style=\"width:50%;\">                             <h1 style=\"font-size:24px;\">Route</h1>                             <ul class=\"route-sortable route-event-list\"></ul>                         </div>                     </div>                 </div>                 <div class=\"modal-footer\"><button class=\"btn btn-default\" type=\"button\" data-dismiss=\"modal\">Close</button><button class=\"btn btn-primary\" type=\"button\" id=\"add-route\" style=\"background-color:#337ab7;\">Add </button></div>             </div>         </div>     </div>     <script defer src=\"https://maps.googleapis.com/maps/api/js?key=AIzaSyDOArxJo-qSYvIVy-r13e57RxHnCgAwEBA&callback=initMap&libraries=places\"></script>     <script src=\"https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js\"></script>     <script src=\"https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js\"></script>     <script src=\"static/assets/js/api.js\"></script>     <script src=\"static/assets/js/classes.js\"></script>     <script src=\"static/assets/js/dummy-server.js\"></script>     <script src=\"static/assets/js/jquery-ui.min.js\"></script>     <script src=\"static/assets/js/PhotoGallery.js\"></script>     <script src=\"static/assets/js/various-plans.js\"></script> </body>  </html> ";
},

planPOST: function(json) {
  var plan = Object.assign({}, json);
  plan.id = this.plans.length;
  plan.creationTime = (new Date()).getTime();
  this.plans.push(plan);
  return plan;
},

planGETjoin: function(joinId) {
  return this.plans[id];
},

///////////////////////LOCATION///////////////////////


/*Example event object structure
Whats stored in events[]
var egevent = {
id: 0,
planid: 0,
name: "location",
locationid: "dfsafs",
votes: 0
};*/

eventGETid: function(id, userid) {
  var result = Object.assign({}, this.events[id]);
  if(this.events[id] === undefined)
  return undefined;
  result.userVoteState = this.getUserVoteState(id, userid, true);
  return result;
},

eventGETplanid: function(planid, userid) {
  var requestTime = (new Date()).getTime();
  var topRoute;
  if(requestTime > this.plans[planid].routeVoteCloseTime) {
    this.routes.forEach(function(r) {
      if(topRoute === undefined || r.votes > topRoute.votes)
      topRoute = r;
    });

    if(topRoute === undefined) {
      //No routes added
      return {result: []};
    }
  }


  var planEvents = [];
  for(var i = 0; i < this.events.length; i++) {
    var e = this.eventGETid(i, userid);
    if(e.planid === planid) {
      if(requestTime <= this.plans[planid].eventVoteCloseTime) {
        planEvents.push(e);
      } else if(requestTime > this.plans[planid].routeVoteCloseTime) {
        if(topRoute.eventidList.includes(e.id))
        planEvents.push(e);
      } else {
        if(e.votes >=0)
        planEvents.push(e);
      }
    }
  }
  return {result: planEvents};
},

eventPOST: function(json, userid) {
  //Clone
  var event = Object.assign({}, json);
  event.id = this.events.length;
  event.votes = 0;
  this.events.push(event);
  //Create entry in array if it doesnt exist
  this.getUserVoteState(event.id, userid, true);
  this.userEventVotes[userid][event.id] = 0;
  return this.eventGETid(event.id, 0);
},

eventPATCH: function(json, id, userid) {
  if(this.events.length > id && (new Date()).getTime() <= this.plans[this.events[id].planid].eventVoteCloseTime) {
    var voteState = this.getUserVoteState(id, userid, true);
    if(json.vote === 1) {
      //Sent upvote
      if(voteState <= 0) {
        //Add 1 when neutral (state=0) and 2 when down (state=-1)
        this.events[id].votes+= (1 - voteState);
      }

    } else if(json.vote === -1) {
      //Sent downvote
      if(voteState >= 0) {
        //Take 1 when neutral (state=0) and 2 when up (state=1)
        this.events[id].votes-= (1 + voteState);
      }
    } else {
      //Sent vote reset
      if(voteState > 0) {
        this.events[id].votes--;
      } else if(voteState < 0) {
        this.events[id].votes++;
      }
    }
    this.userEventVotes[userid][json.id] = json.vote;
  }
},

////////////////////////ROUTES////////////////////////


/*Example route object structure
Whats stored in routes[]
var egroute = {
id: 0,
planid: 0,
name: "route",
eventIdList: [],
votes: 0
};*/

routeGETid: function(id, userid) {
  var result = Object.assign({}, this.routes[id]);
  if(this.routes[id] === undefined)
  return undefined;
  result.userVoteState = this.getUserVoteState(id, userid, false);
  return result;
},

routeGETplanid: function(planid, userid) {
  var requestTime = (new Date()).getTime();
  var planRoutes = [];
  var topRoute;
  for(var i = 0; i < this.routes.length; i++) {
    var r = this.routeGETid(i, userid);
    if(r.planid === planid) {
      if(requestTime <= this.plans[planid].routeVoteCloseTime) {
        planRoutes.push(r);
      } else {
        if(topRoute === undefined || r.votes > topRoute.votes)
        topRoute = r;
      }
    }
  }
  if(requestTime > this.plans[planid].routeVoteCloseTime)
  return {result: [topRoute]};
  return {result: planRoutes};
},

routePOST: function(json, userid) {
  //Clone
  var route = Object.assign({}, json);
  route.id = this.routes.length;
  route.votes = 0;
  this.routes.push(route);
  //Create entry in array if it doesnt exist
  this.getUserVoteState(json.id, userid, false);
  this.userRouteVotes[userid][route.id] = 0;
  return this.routeGETid(route.id, 0);
},

routePATCH: function(json, id, userid) {
  if(this.routes.length > id) {
    var voteState = this.getUserVoteState(id, userid, false);
    if(json.vote === 1) {
      //Sent upvote
      if(voteState <= 0) {
        //Add 1 when neutral (state=0) and 2 when down (state=-1)
        this.routes[id].votes+= (1 - voteState);
      }

    } else if(json.vote === -1) {
      //Sent downvote
      if(voteState >= 0) {
        //Take 1 when neutral (state=0) and 2 when up (state=1)
        this.routes[id].votes-= (1 + voteState);
      }
    } else {
      //Sent vote reset
      if(voteState > 0) {
        this.routes[id].votes--;
      } else if(voteState < 0) {
        this.routes[id].votes++;
      }
    }
    this.userRouteVotes[userid][id] = json.vote;
  }
}
};
