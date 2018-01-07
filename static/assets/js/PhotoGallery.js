class PhotoGallery {
    constructor(placePhotos, maxwidth)  {
        this.photoUrls = [];
        this.index = 0;
        this.count = 0;
        this.maxwidth = maxwidth;

        this.dom = $("<div>", {"class": "photo-gallery"});

        var self = this;
        placePhotos.forEach(function(placePhoto) {
            var url = placePhoto.getUrl({
                maxWidth: maxwidth
            });
            self.photoUrls.push(url);
            $("<img>", {"class": "photo-gallery-entry entry-" + self.count, "src": url}).appendTo(self.dom);
            self.count++;
        });

        this.prevButton = $("<div>", {"class": "photo-gallery-prev"}).hide().html("<div class=\"pg-icon\"></div>").appendTo(this.dom);
        this.nextButton = $("<div>", {"class": "photo-gallery-next"}).html("<div class=\"pg-icon\"></div>").appendTo(this.dom);

        this.nextButton.off("click").click(function(){ self.scrollNext(); });
        this.prevButton.off("click").click(function(){ self.scrollPrev(); });
    }

    addPhoto(placePhoto) {
        var url = placePhoto.getUrl({
            maxWidth: maxwidth
        });
        this.photoUrls.push(url);
        $("<img>", {"class": "photo-gallery-entry entry-" + this.count, "src": url}).appendTo(this.dom);
        this.count++;
    }

    render(container) {
        //Render the photo gallery in a given jQuery object
        container.append(this.dom);
        return this;
    }

    scrollNext() {
        this.prevButton.show();

        if(this.index === this.count-2)
            this.nextButton.hide();

        if(this.index < this.count-1) {
            this.index++;
            var self = this;
            this.repositionGallery();
        }
    }

    scrollPrev() {
        this.nextButton.show();

        if(this.index === 1)
            this.prevButton.hide();

        if(this.index > 0) {
            this.index--;
            this.repositionGallery();
        }
    }

    repositionGallery() {
      var self = this;
      return new Promise(function(resolve) {
        var currEntry = self.dom.find(".entry-" + self.index);
        var distance = currEntry.position().left; //Move images so current is at left side of window
        distance -= (self.dom.width() - currEntry.width()) / 2; //Center Image
        distance -= 12; //Adjust for entry margins
        self.dom.find(".photo-gallery-entry").animate({ left: "-=" + distance }, 400, resolve);
      });
    }
}
