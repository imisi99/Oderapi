# Oderapi
This is an orderapi created for fun using FastAPI and Sqlite
It uses 0auth for its authorization and jwt for it's authentication
All it's routes are locked and requires a user to be logged in (all routes can be seen using the FASTAPI swagger UI)
The user needs to signup first, then log in with 0auth to have access to all routes 
User's data are protected and secured as there is a verification process for only the logged in user details to be shown, displayed and a user can act only on his own order 
