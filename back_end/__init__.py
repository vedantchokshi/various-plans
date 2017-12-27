
def init(app):
    import api, db
    db.init(app)
    api.init(app)
