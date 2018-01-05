var googleLoginListeners = {
  onSignIn: [],
  onSignOut: []
};

function initGapiSignin() {
  //Google Sign in
  gapi.auth2.init({
    client_id: "952476275187-ef3icj10cn4ptsl3ehs3jcg3tdeff0pv.apps.googleusercontent.com"
  }).then(function(){
    //On Google Auth Load Success:
    var auth2 = gapi.auth2.getAuthInstance();
    //Center Google Login Button
    $(".abcRioButton").css("margin", "auto");
    if(auth2.isSignedIn.get()) {
      onGSignInChange(true);
    } else {
      //Show Google API Sign In Button
      $(".g-signin2").fadeIn();
      //Setup listener for Login/Logout
      auth2.isSignedIn.listen(onGSignInChange);
    }
  }, function(){
    //On Error:
    //TODO: Error Handling
  });

}

function onGSignInChange(signedin) {
  if(signedin === true) {
    googleLoginListeners.onSignIn.forEach(function(listener) {
      listener();
    });
  } else {
    googleLoginListeners.onSignOut.forEach(function(listener) {
      listener();
    });
  }
}
