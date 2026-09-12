schemas.py help us define a structure, a confined skeleton for our entities
In this case, Users and their posts.
we use Pydantic for schema validation as our go to framework since its a standard
Our Pydantic implementation guards the entry and exit of data from our application DB to/from user
If any incoming data which is supposed to wear one schema as costume, tries to entry with some additional/less clothes, our guard is advised to throw 422 Status code to the end user

We have UserBase, PostBase which act as base model for User creation and Post Creation

We also use UserPublic and UserPrivate to manage the data accoording to security permission to user
UserPublic makes sure id, username, and profile pic are allowed
but not email, for that we have UserPrivate schema

similarly PostCreate helps allowing entry of any payload which only has title and content (both must be there)
and PostUpdate inherits directly from BaseModel so anyone carrying this outfit is allowed to have either of both fields or both

we also have Token costume that is specifically created for outgoing payloads from server
It has access token and the token type