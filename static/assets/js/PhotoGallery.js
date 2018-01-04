class PhotoGallery {
    constructor(placePhotos, maxwidth)  {
        this.photoUrls = [];
        this.index = 0;
        this.count = 0;
        this.maxwidth = maxwidth;
        
        this.dom = $("<div>", {"class": "photo-gallery"});
        this.prevButton = $("<div>", {"class": "photo-gallery-prev"}).hide().appendTo(this.dom);
        
        var self = this;
        placePhotos.forEach(function(placePhoto) {
            var url = placePhoto.getUrl({
                maxWidth: maxwidth
            });
            self.photoUrls.push(url);
            $("<img>", {"class": "photo-gallery-entry-" + self.count, "src": url}).hide().appendTo(self.dom);
            self.count++;
        });
        
        this.nextButton = $("<div>", {"class": "photo-gallery-next"}).appendTo(this.dom);
        
        this.dom.find(".photo-gallery-entry-0").show();
        this.nextButton.off("click").click(function(){ self.scrollNext(); });
        this.prevButton.off("click").click(function(){ self.scrollPrev(); });
    }
    
    addPhoto(placePhoto) {
        var url = placePhoto.getUrl({
            maxWidth: maxwidth
        });
        this.photoUrls.push(url);
        $("<img>", {"class": "photo-gallery-entry-" + this.count, "src": url}).hide().appendTo(this.dom);
        this.count++;
    }
    
    render(container) {
        //Render the photo gallery in a given jQuery object
        container.append(this.dom);
    }
    
    scrollNext() {
        this.prevButton.show();
        
        if(this.index === this.count-2)
            this.nextButton.hide();
        
        if(this.index < this.count-1) {
        var self = this;
            this.dom.find(".photo-gallery-entry-" + this.index).fadeOut(400, function() {
                self.index++;
                self.dom.find(".photo-gallery-entry-" + self.index).fadeIn();
            });
        }
    }
    
    scrollPrev() {
        this.nextButton.show();
        
        if(this.index === 1)
            this.prevButton.hide();
        
        if(this.index > 0) {
        var self = this;
            this.dom.find(".photo-gallery-entry-" + this.index).fadeOut(400, function() {
                self.index--;
                self.dom.find(".photo-gallery-entry-" + self.index).fadeIn();
            });
        }
    }
}