-- Forgot password endpoint
When user clicks forgot password, we immediately return the generic message, saying if u are a real deal, one of iur dudes will send u an email

by this time one thing happens in bg

we get user's email and check if user is present in DB or not

If so, our main shit starts wherein we first invalidate any stale token that might be there for this user in db (for password reset) so there is no danger of multiple requests with none actually being real, then we generate one random ass token,

hash it, add some expiry shit to it, stire this HASHED token in our reste password table and commit this shit

now u might ask what about random ass token?
yeah so then come sthe fonal nail, which is sending user an email
this email
In this email we siend that randoma ass token to send_password_reset_email
whcih uses it internally to shoot out mail using any smtp shit
everything from `result = await db.execute(...)` down to await db.commit() happens synchronously inside the request before the background task runs.

-- Reset Password endpoint
