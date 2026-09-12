## TO REMEMBER - 

### ASYNC DB CALLS WITH AND WITHOUT EAGER LOADING
Basic model fields (id, name, created_at): Safe to access without eager loading.

Relationship fields (user.posts, post.author, user.comments): Crash the server when accessed unless you explicitly requested them upfront using selectinload