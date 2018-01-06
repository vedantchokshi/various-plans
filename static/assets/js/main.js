var redirectToMain = function() { window.location = "/"; }

googleLoginListeners.onNotSignedIn.push(redirectToMain);
googleLoginListeners.onSignOut.push(redirectToMain);
