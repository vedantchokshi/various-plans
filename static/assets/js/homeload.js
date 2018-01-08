//Plan Entry UI
class PlanEntry {

  constructor(plan, linkable){
    if(linkable)
      this.entry = $("<a>", {"class" : "plan-entry card-ui", "href": "/" + plan.id});
    else
      this.entry = $("<a>", {"class" : "plan-entry dead card-ui"});
    this.name = $("<span>", {"class" : "plan-name"}).html("<strong>" + plan.name + "</strong>").appendTo(this.entry);
    this.joinidOrExpiryReason = $("<span>", {"class" : "plan-join-code", text: plan.joinid}).appendTo(this.entry);
    this.endTime = $("<span>", {"class" : "plan-end-time", text: new Date(plan.endTime*1000).toLocaleString()}).appendTo(this.entry);
  }

  render(container) {
    this.entry.appendTo(container);
  }
}

//Runs when page first properly loads
$(document).ready(function() {

  $("#sign-out").click(function() {
    gapi.auth2.getAuthInstance().signOut();
  });

  //Add datepickers to create modal
  $( ".datepicker" ).datetimepicker({
     minDate: 0,
     dateFormat: 'd M y',
	   timeFormat: 'HH:mm z',
     showOn: "button",
     buttonImage: "../static/assets/img/calendar.svg",
     buttonImageOnly: true,
     buttonText: "Select date"
  });

  $("#create-plan-modal").on("show.bs.modal", function() {
    $("#create-plan-modal").find(".error-message").hide();
  });

  $("#join-plan-modal").on("show.bs.modal", function() {
    var joinPlanModal = $("#join-plan-modal");
    joinPlanModal.find("#join-code").val("");
    joinPlanModal.find(".error-message").hide();
  });

  //Functionality for create plan button
  $("#create-plan").click(function() {
    var name = $("#planTextBox").val();

    var eventVC = $("#locationVoteCloseText").datetimepicker("getDate");
    //If null pass it to back end anyway, backend will error report
    if(eventVC !== undefined && eventVC !== null)
      eventVC = Math.floor(eventVC.getTime() / 1000);

    var routeVC = $("#routeVoteCloseText").datetimepicker("getDate");
    //If null pass it to back end anyway, backend will error report
    if(routeVC !== undefined && routeVC !== null)
      routeVC = Math.floor(routeVC.getTime() / 1000);

    var planEnd = $("#planCloseText").datetimepicker("getDate");
    //If null pass it to back end anyway, backend will error report
    if(planEnd !== undefined && planEnd !== null)
      planEnd = Math.floor(planEnd.getTime() / 1000);

    api.plan.create(name, eventVC, routeVC, planEnd).then(function(plan) {
      //Load Plan Page
      redirectWithFreshToken("/" + plan.id);
    },
    function(error_obj) {
      console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
      var createPlanModal = $("#create-plan-modal");
      createPlanModal.find(".error-message").html(error_obj.message);
      createPlanModal.find(".error-message").hide().fadeIn();
    });
  });

  //Functionality for the Join Plan 'Add' button
  $("#join-plan-add").click(function() {
    var joinId = $("#join-code").val();
    $("#join-code").val("");
    api.plan.join(joinId).then(function(plan) {
      var activePlan = displayPlan(plan);

      if(activePlan) {
        setupActiveList();
        //Minimize archive list until clicked on
        $("#archived-plan-list-wrapper").slideUp();
        if($("#archived-plan-list-header").is(":visible")) {
          setupBothLists();
          $("#active-plan-list-header").addClass("expanded");
          $("#archived-plan-list-header").removeClass("expanded");
        }
        //Scroll to bottom of active list
        $("#active-plan-list").scrollTop($("#active-plan-list").prop("scrollHeight"));

      } else {
        setupArchiveList();
        //Minimize active list until clicked on
        $("#active-plan-list-wrapper").slideUp();
        if($("#active-plan-list-header").html() === "Active Plans") {
          setupBothLists();
          $("#active-plan-list-header").removeClass("expanded");
          $("#archived-plan-list-header").addClass("expanded");
        }
        //Scroll to bottom of archive list
        $("#archived-plan-list").scrollTop($("#archived-plan-list").prop("scrollHeight"));
      }
    },
    function(error_obj){
      console.error("API ERROR " + error_obj.status_code + ": " + error_obj.message);
      $("#join-plan-modal").find(".error-message").html(error_obj.message);
      $("#join-plan-modal").find(".error-message").hide().fadeIn();
    });
  });
});

googleLoginListeners.onLoad.push(function() {
  //Center Google Login Button
  $("#signin-button").click(function() {
    gapi.auth2.getAuthInstance().signIn({
      ux_mode: "popup",
      prompt: "select_account"
    });
  });
});

googleLoginListeners.onNotSignedIn.push(function() {
  //Show Google API Sign In Button
  $("#signin-button").fadeIn();
});

googleLoginListeners.onSignIn.push(function() {
  //Show button controls
  $("#signin-button").fadeOut(400, function() {
    $("#button-wrapper").fadeIn();
    api.updateVPToken();
    displayUsersPlans();
  });

  //Show profile in navbar
  var userProfile = gapi.auth2.getAuthInstance().currentUser.get().getBasicProfile();
  $("#name").html("<strong>" + userProfile.getGivenName() + "</strong><i class=\"glyphicon glyphicon-user\"></i>");
  $("#email").html(userProfile.getEmail());
  $("#user-info-button").fadeIn();
});

googleLoginListeners.onSignOut.push(function() {
  //Hide button controls
  $("#button-wrapper").fadeOut(400, function() {
    $("#signin-button").fadeIn();
  });
  $("#user-info-button").fadeOut();
  setdownActiveList();
  setdownArchiveList();
});

function displayPlan(plan) {
  var currTime = Math.floor(new Date().getTime() /1000);
  var activePlan = true;
  var openable = true;

  //Note reason for plan expiry
  if(currTime > plan.endTime && plan.routes_count === 0) {
    activePlan = false;
    openable = false;
    plan.joinid = "No Routes Added";
  } else if(currTime > plan.endTime) {
    activePlan = false;
    plan.joinid = "Time Limit Exceeded";
  } else if(currTime > plan.routeVoteCloseTime && plan.routes_count === 0) {
    activePlan = false;
    openable = false;
    plan.joinid = "No Routes Added";
  } else if(currTime > plan.eventVoteCloseTime && plan.events_count_positive === 0) {
    activePlan = false;
    openable = false;
    plan.joinid = "No Events Preferred";
  }

  //Place plan entry in correct list
  var targetList = activePlan ? $("#join-plan-modal").find("#active-plan-list") : $("#join-plan-modal").find("#archived-plan-list");
  new PlanEntry(plan, openable).render(targetList);

  return activePlan;
}

function displayUsersPlans() {
  //Add user's current plans to join modal
  api.user.plans().then(function(results) {
    var noActivePlans = 0, noArchivedPlans = 0;
    results.results.forEach(function(plan) {

      var activePlan = displayPlan(plan);

      if(activePlan)
        noActivePlans++;
      else
        noArchivedPlans++;
    });

    //If there are no active plans
    if(results.results.length === 0 || noActivePlans === 0) {
      setdownActiveList();
      $("#active-plan-list-header").html("You are not currently involved in any active plans.");
    } else {
      setupActiveList();
    }
    //If there are no archived plans
    if(noArchivedPlans === 0) {
      setdownArchiveList();
    } else {
      setupArchiveList();
    }

    //If there are both archived and active plans
    if(noActivePlans > 0 && noArchivedPlans > 0) {
      setupBothLists();
      //Maximize active list and minimize archived list by default
      $("#active-plan-list-wrapper").slideDown();
      $("#archived-plan-list-wrapper").slideUp();
      $("#active-plan-list-header").addClass("expanded");
      $("#archive-plan-list-header").removeClass("expanded");
    }
  },
  function(error_obj){
    console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
    //No errors intended for users sent here.
  });
}

//Set up Join plan modal UI so active list is visible
function setupActiveList() {
  $("#active-plan-list-header").html("Active Plans");
  $("#active-plan-list-titles").show();
  $("#active-plan-list-wrapper").slideDown();
}

function setdownActiveList() {
  //Remove expandable classes if they have them
  var activePlanHeader = $("#active-plan-list-header");
  activePlanHeader.removeClass("expandable");
  //Hide list titles
  activePlanHeader.html("Loading...");
  $("#active-plan-list-titles").hide();
  //Remove listener
  activePlanHeader.off("click");
  //Clear list
  $("#join-plan-modal").find("#active-plan-list").empty();
}

//Set up Join plan modal UI so archive list is visible
function setupArchiveList() {
  $("#archived-plan-list-header").show();
  $("#archived-plan-list-titles").show();
  $("#archived-plan-list-wrapper").slideDown();
}

function setdownArchiveList() {
  //Remove expandable classes if they have them
  var archivePlanHeader = $("#archived-plan-list-header");
  archivePlanHeader.removeClass("expandable");
  //Hide list titles
  archivePlanHeader.hide();
  $("#archived-plan-list-titles").hide();
  //Remove listener
  archivePlanHeader.off("click");
  //Clear list
  $("#join-plan-modal").find("#archived-plan-list").empty();
}

//Set up Join Plan modal UI so both lists are usable
function setupBothLists() {
  var activePlanHeader = $("#active-plan-list-header");
  var archivePlanHeader = $("#archived-plan-list-header");

  activePlanHeader.addClass("expandable");
  archivePlanHeader.addClass("expandable");

  activePlanHeader.off("click").click(function() {
    activePlanHeader.addClass("expanded");
    archivePlanHeader.removeClass("expanded");

    $("#active-plan-list-wrapper").slideDown();
    $("#archived-plan-list-wrapper").slideUp();
  });

  archivePlanHeader.off("click").click(function() {
    activePlanHeader.removeClass("expanded");
    archivePlanHeader.addClass("expanded");

    $("#active-plan-list-wrapper").slideUp();
    $("#archived-plan-list-wrapper").slideDown();
  });
}

function redirectWithFreshToken(path) {
  api.updateVPToken();
  window.location = path;
}
