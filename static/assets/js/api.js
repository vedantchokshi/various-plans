//Static object for interacting with backend API
var api = {
    //Calls to /api/user
    user: {
      //Gets a list of plans for the user identified by the Google API token in the cookie header of this request
      plans: function() {
          return api.ajax("/api/user/plans", "GET");
      }
    },
    //Calls to /api/plan/*
    plan: {
        //Gets a plan by its ID
        get: function(id) {
            return api.ajax("/api/plan/" + id, "GET");
        },
        //Creates a new plan on the server
        create: function(name, eventVoteCloseTime, routeVoteCloseTime, endTime) {
            var json = {name: name, eventVoteCloseTime: eventVoteCloseTime, routeVoteCloseTime: routeVoteCloseTime, endTime: endTime};
            return api.ajax("/api/plan", "POST", json);
        },
        //Gets all events associated with a plan of a certain ID
        //(Server only returns positive voted plans after events voting is complete)
        getEvents: function(planId) {
            return api.ajax("/api/plan/" + planId + "/events", "GET");
        },
        //Gets all routes associated with a plan of a certain ID
        getRoutes: function(planId) {
            return api.ajax("/api/plan/" + planId + "/routes", "GET");
        },
        //Adds the user identified by the Google API token in the cookie header of this request to the plan identified by joinId
        join: function(joinId) {
            return api.ajax("/api/plan/join/" + joinId, "GET");
        }
    },
    //Calls to /api/event/*
    event: {
        //Gets an event by its unique ID
        get: function(id) {
            return api.ajax("/api/event/" + id, "GET");
        },
        //Creates a new event on the server
        create: function(name, planId, locationId) {
            var json = {name: name, planid: planId, locationid: locationId};
            return api.ajax("/api/event", "POST", json);
        },
        //Upvote the event of the given id
        upvote: function(id){
            return api.ajax("/api/event/" + id + "/vote", "POST", {vote: 1});
        },
        //Downvote the event of the given id
        downvote: function(id) {
            return api.ajax("/api/event/" + id + "/vote", "POST", {vote: -1});
        },
        //Reset the vote on the event of the given id
        resetvote: function(id) {
            return api.ajax("/api/event/" + id + "/vote", "POST", {vote: 0});
        }
    },
    //Calls to /api/route/*
    route: {
        //Gets a route from its unique ID
        get: function(id) {
            return api.ajax("/api/route/" + id, "GET");
        },
        //Creates new route on server
        create: function(name, planId, eventList) {
            var json = {name: name, planid: planId, eventidList: eventList};
            return api.ajax("/api/route", "POST", json);
        },
        //Upvote the route of the given id
        upvote: function(id){
            return api.ajax("/api/route/" + id + "/vote", "POST", {vote: 1});
        },
        //Downvote the route of the given id
        downvote: function(id) {
            return api.ajax("/api/route/" + id + "/vote", "POST", {vote: -1});
        },
        //Reset the vote on the route of the given id
        resetvote: function(id) {
            return api.ajax("/api/route/" + id + "/vote", "POST", {vote: 0});
        }
    },

    ajax: function(url, method, json) {
      if(json === undefined || json === null)
        json = {};
      return new Promise(function(success, error) {
        $.ajax({
          url: url,
          method: method,
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          data: JSON.stringify(json),
          success: success,
          error: function(response) {
            error(response.responseJSON);
          }
        });
      });
    }
};
