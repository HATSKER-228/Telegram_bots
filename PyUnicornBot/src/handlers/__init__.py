from . import common, baby, numbers, admin

routers = [admin.router,
           common.router,
           baby.router,
           numbers.router]
