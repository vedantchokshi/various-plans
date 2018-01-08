
//Requires modal HTML code on page modal is shown on.
var popupModal = {
  inited: false,

  /**
   * Displays a popup modal with a specified title and Message
   * Returns a promise that is fulfilled when the modal is closed.
   */
  show: function(title, message) {
    if(!this.inited)
      this.init();
    return new Promise(function(resolve) {

      var popup = $("#popup-modal");
      popup.find("#popup-modal-title").html(title);
      popup.find("#popup-modal-message").html(message);
      popup.modal("show");

      popup.on("hide.bs.modal", resolve);
    });
  },

  /**
   * Adds HTML code to body required by popup modal
   */
  init: function() {
    if(!this.inited)
      $("<div>").html("<div class=\"modal fade\" role=\"dialog\" tabindex=\"-1\" id=\"popup-modal\"><div class=\"modal-dialog\" style=\"width: 25%;\" role=\"document\"><div class=\"modal-content\"><div class=\"modal-header\"><button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">×</span></button><h3 class=\"modal-title\" id=\"popup-modal-title\"></h3></div><div class=\"modal-body\"><p id=\"popup-modal-message\"></p></div><div class=\"modal-footer\"><button class=\"btn btn-primary\" id=\"popup-modal-ok\" data-dismiss=\"modal\" type=\"button\">Ok</button></div></div></div></div>").appendTo(document.body);
  }
};
