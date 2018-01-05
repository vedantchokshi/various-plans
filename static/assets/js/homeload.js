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

  
});

googleLoginListeners.onSignIn.push(function() {
  //Show button controls
  $(".g-signin2").fadeOut(400, function() {
    $("#button-wrapper").fadeIn();
    updateVPToken();
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

}
