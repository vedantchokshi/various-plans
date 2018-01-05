var currTimeForDummy = Math.floor((new Date()).getTime() / 1000);
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
  return this.plans[id];
},

planPOST: function(json) {
  var plan = Object.assign({}, json);
  plan.id = this.plans.length;
  plan.startTime = Math.floor((new Date()).getTime() / 1000);
  plan.joinid = Math.floor(Math.random()*100000000000000000);
  this.plans.push(plan);
  return plan;
},

planGETjoin: function(joinId) {

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
  var requestTime = Math.floor((new Date()).getTime() / 1000);
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
  if(this.events.length > id && Math.floor((new Date()).getTime() / 1000) <= this.plans[this.events[id].planid].eventVoteCloseTime) {
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
  var requestTime = Math.floor((new Date()).getTime() / 1000);
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
