//Static object for interacting with backend API
var api = {
    //Calls to /api/plan/*
    plan: {
        //Gets a plan by its ID
        get: function(id) {
            //TODO: replace with AJAX call
            var plan = dummyServer.planGET(id);
            return plan;
        },
        //Creates a new plan on the server
        create: function(name, locationVoteCloseTime, routeVoteCloseTime) {
            var json = {name: name, locationVoteCloseTime: locationVoteCloseTime, routeVoteCloseTime: routeVoteCloseTime};
            //TODO: replace with AJAX call
            var planResponse = dummyServer.planPOST(json);
            return planResponse;
        },
        //Gets all events associated with a plan of a certain ID
        //(Server only returns positive voted plans after events voting is complete)
        getEvents: function(planId) {
            //TODO: replace with AJAX call
            var response = dummyServer.eventGETplanid(planId, 0);
            return response.result;
        },
        //Gets all routes associated with a plan of a certain ID
        getRoutes: function(planId) {
            //TODO: replace with AJAX call
            var response = dummyServer.routeGETplanid(planId, 0);
            return response.result;
        }
    },
    //Calls to /api/event/*
    event: {
        //Gets an event by its unique ID
        get: function(id) {
            //TODO: replace with AJAX call
            var event = dummyServer.eventGETid(id, 0);
            return event;
        },
        //Creates a new event on the server
        create: function(name, planId, locationId) {
            var json = {name: name, planid: planId, locationid: locationId};
            //TODO: replace with AJAX call
            var eventResponse = dummyServer.eventPOST(json, 0);
            return eventResponse;
        },
        //Upvote the event of the given id
        upvote: function(id){
            var json = {vote: 1};
            //TODO: replace with AJAX call
            dummyServer.eventPATCH(json, id, 0);
        },
        //Downvote the event of the given id
        downvote: function(id) {
            var json = {vote: -1};
            //TODO: replace with AJAX call
            dummyServer.eventPATCH(json, id, 0);
        },
        //Reset the vote on the event of the given id
        resetvote: function(id) {
            var json = {vote: 0};
            //TODO: replace with AJAX call
            dummyServer.eventPATCH(json, id, 0);
        }
    },
    //Calls to /api/route/*
    route: {
        //Gets a route from its unique ID
        get: function(id) {
            //TODO: replace with AJAX call
            var route = dummyServer.routeGETid(id, 0);
            return route;
        },
        //Creates new route on server
        create: function(name, planId, eventList) {
            var json = {name: name, planid: planId, eventidList: eventList};
            //TODO: replace with AJAX call
            var routeResponse = dummyServer.routePOST(json, 0);
            return routeResponse;
        },
        //Upvote the route of the given id
        upvote: function(id){
            var json = {vote: 1};
            //TODO: replace with AJAX call
            dummyServer.routePATCH(json, id, 0);
        },
        //Downvote the route of the given id
        downvote: function(id) {
            var json = {vote: -1};
            //TODO: replace with AJAX call
            dummyServer.routePATCH(json, id, 0);
        },
        //Reset the vote on the route of the given id
        resetvote: function(id) {
            var json = {vote: 0};
            //TODO: replace with AJAX call
            dummyServer.routePATCH(json, id, 0);
        }
    }
};
