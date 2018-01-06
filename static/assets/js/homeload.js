//Plan Entry UI
class PlanEntry {

  constructor(plan){
    this.entry = $("<div>", {"class" : "plan-entry"});
    this.name = $("<span>", {"class" : "plan-name", text: plan.name}).appendTo(this.entry);
    this.startTime = $("<span>", {"class" : "plan-start-time", text: new Date(plan.startTime*1000).toLocaleString()}).appendTo(this.entry);
    this.endTime = $("<span>", {"class" : "plan-end-time", text: new Date(plan.endTime*1000).toLocaleString()}).appendTo(this.entry);

    this.openButton = $("<button>", {"class" : "plan-open-button", text: "OPEN"})
      .click(function() {
        redirectWithFreshToken("/" + plan.id);
      })
      .appendTo(this.entry);
  }

  render(container) {
    this.entry.appendTo(container);
  }
}

//Runs when page first properly loads
$(document).ready(function() {
  //Add datepickers to create modal
  $( ".datepicker" ).datetimepicker({
     minDate: 0,
	   timeFormat: 'HH:mm z',
     showOn: "button",
     buttonImage: "../static/assets/img/calendar.svg",
     buttonImageOnly: true,
     buttonText: "Select date"
  });

  //Functionality for create plan button
  $("#create-plan").click(function() {
    //TODO: Feedback for empty fields
    var name = $("#planTextBox").val();
    var eventVC = Math.floor($("#locationVoteCloseText").datetimepicker("getDate").getTime() / 1000);
    var routeVC = Math.floor($("#routeVoteCloseText").datetimepicker("getDate").getTime() / 1000);
    var planEnd = Math.floor($("#planCloseText").datetimepicker("getDate").getTime() / 1000);
    api.plan.create(name, eventVC, routeVC, planEnd).then(function(plan) {
      //Load Plan Page
      redirectWithFreshToken("/" + plan.id);
    },
    function(error_obj) {
      console.error("API ERROR CODE " + error_obj.status_code + ": " + error_obj.message);
    });
  });

  //Functionality for the Join Plan 'Add' button
  $("#join-plan-add").click(function() {
    //TODO: Feedback for empty field
    var joinId = $("#join-code").val();
    api.plan.join(joinId).then(function(plan) {
      $("#plan-list-header").html("Your Plans");
      new PlanEntry(plan).render($("#join-plan-modal").find(".modal-body"));
    },
    function(error_obj){
      //TODO: Handle Join Errors
    });
  });
});

googleLoginListeners.onLoad.push(function() {
  //Center Google Login Button
  $(".abcRioButton").css("margin", "auto");
});

googleLoginListeners.onNotSignedIn.push(function() {
  //Show Google API Sign In Button
  $(".g-signin2").fadeIn();
});

googleLoginListeners.onSignIn.push(function() {
  //Show button controls
  $(".g-signin2").fadeOut(400, function() {
    $("#button-wrapper").fadeIn();
    api.updateVPToken();
    displayUsersPlans();
  });
});

googleLoginListeners.onSignOut.push(function() {
  //Hide button controls
  $("#button-wrapper").fadeOut(400, function() {
    $(".g-signin2").fadeIn();
  });
});

function displayUsersPlans() {
  //Add user's current plans to join modal
  api.user.plans().then(function(results) {
    if(results.results.length === 0)
      $("#plan-list-header").html("You are not currently on any active plans.");
    results.results.forEach(function(plan) {
      new PlanEntry(plan).render($("#join-plan-modal").find(".modal-body"));
    });
  },
  function(error_obj){
    //TODO: Handle Join Errors
  });
}

function redirectWithFreshToken(path) {
  api.updateVPToken();
  window.location = path;
}
