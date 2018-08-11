def index():
    
    if auth.is_logged_in():
        response.flash = T("WELCOME")
        
        if len(request.args): 
            page=int(request.args[0])
        else: 
            page=0
        items_per_page=4
        limitby=(page*items_per_page,(page+1)*items_per_page+1)
        rows=db(db.image.id>0).select(db.image.ALL,limitby=limitby,orderby=~db.image.date)
        return dict(rows=rows,page=page,items_per_page=items_per_page)
    else:
        redirect(URL('default','user'))

def mine():
    if auth.is_logged_in():
        if len(request.args): 
            page=int(request.args[0])
        else:
            page=0
        items_per_page=4
        limitby=(page*items_per_page,(page+1)*items_per_page+1)
        rows=db((db.image.id>0)&(db.image.email==auth.user.email)).select(db.image.ALL,limitby=limitby,orderby=~db.image.date)
        return dict(rows=rows,page=page,items_per_page=items_per_page)

def user():
   
        return dict(form=auth())
    

def create():
    if auth.is_logged_in():
        db.image.date.default = request.now
        db.image.date.writable = db.image.date.readable = False
        form = SQLFORM(db.image).process()
        if form.accepted:
            response.flash="recipe added"
   
        return dict(form=form)
    else:
        redirect(URL('default','user'))


def show():
    image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    db.post.recipe.default = image.id
    form = SQLFORM(db.post)
    
    if form.process().accepted:
        response.flash = 'your comment is posted'
    comments = db(db.post.recipe==image.id).select()
    return dict(image=image, comments=comments, form=form)

def edit():
    this_page = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.image, this_page,deletable=True).process()
    if form.accepted:
        session.flash ="recipe updated"
        redirect(URL('default','mine'))
    return dict(form=form)


@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.grid(db.image)
    return locals()

def download():
    return response.download(request, db)
