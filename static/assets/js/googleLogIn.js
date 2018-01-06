var googleLoginListeners = {
  onLoad: [], //Called when Google Login API is finished loading
  onNotSignedIn: [], //Called when the user is not already signed in on page load
  onSignIn: [], //Called when the user signs in or page loads and user is already signed in
  onSignOut: [] //Called when user signs out
};

function initGapiSignin() {
  //Google Sign in
  gapi.auth2.init({
    client_id: "952476275187-ef3icj10cn4ptsl3ehs3jcg3tdeff0pv.apps.googleusercontent.com"
  }).then(function(){
    //On Google Auth Load Success:
    var auth2 = gapi.auth2.getAuthInstance();
    //Setup listener for Login/Logout
    auth2.isSignedIn.listen(onGSignInChange);
    googleLoginListeners.onLoad.forEach(function(listener) {
      listener();
    });
    if(auth2.isSignedIn.get()) {
      onGSignInChange(true);
    } else {
      googleLoginListeners.onNotSignedIn.forEach(function(listener) {
        listener();
      });
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
