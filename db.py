g.db = mysql.connector.connect(
    ...
    port=current_app.config["DATABASE_PORT"],
)
