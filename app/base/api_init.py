# Standard library imports
import os
import importlib

# Third-party imports
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# Local application imports
from base.logger import logger as _logger
from base.dependencies import log_request_info


# Miscellaneous
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

class FastAPIWrapper:

    def __init__(self):
        self.fastapi_app = self.create_app() # fastapi_app has to be the last to be created


    def load_env(self):
        """
        Loads every config file inside config/ in to the environment
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../')
        for root, dirs, files in os.walk(addons_dir):
            if 'tests' in dirs:
                _logger.debug(f"Skipped test dir: {os.path.join(root, 'tests')}")
                dirs.remove('tests')  # Prevent descending into 'tests' directories

            if os.path.basename(root) == 'config':
                _logger.debug(f"Inspecting 'config' folder: {root}")
                
                # Find all *.env files in this folder
                for file in files:
                    if file.endswith('.env'):
                        env_file_path = os.path.join(root, file)
                        _logger.info(f"Found .env file: {env_file_path}")


    def setup_base_routes(self,app: FastAPI) -> None:
        pass

    def setup_addon_routers(self,app: FastAPI) -> None:
        """
            Import all routes using dynamic importing (Reflections)
        """
        self.register_routes(app=app)

    def create_app(self):
        description = f"API"
        fastapi_app = FastAPI(
            title="API",
            openapi_url=f"/openapi.json",
            docs_url="/docs/",
            description=description,
        )
        self.load_env()
        self.setup_base_routes(app=fastapi_app)
        self.setup_addon_routers(app=fastapi_app)
        self.use_route_names_as_operation_ids(app=fastapi_app)
        self.setup_middleware(app=fastapi_app)
        return fastapi_app
    

    def setup_middleware(self,app : FastAPI):
        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:8080",
        ]

        app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_credentials=True,
            allow_origins=origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # NOTE:: Enable this if it need to be exposed to the WAN
        # app.add_middleware(
        #     # Ensures all trafic to server is ssl encrypted or is rederected to https / wss
        #     middleware_class=HTTPSRedirectMiddleware
        # )

    def use_route_names_as_operation_ids(self,app: FastAPI) -> None:
        """
        Simplify operation IDs so that generated API clients have simpler function
        names.

        Should be called only after all routes have been added.
        """
        route_names = set()
        for route in app.routes:
            if isinstance(route, APIRoute):
                if route.name in route_names:
                    raise Exception(f"Route function names {[route.name]} should be unique")
                route.operation_id = route.name
                route_names.add(route.name)



    def include_router_from_module(self,app : FastAPI, module_name: str):
        """
        Import module and check if it contains 'router' attribute.
        if it does include the route in the fastapi app 
        """
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, 'router') and hasattr(module, 'dependency'):
                app.include_router(
                    router=module.router,
                    dependencies=module.dependency.append(
                        Depends(dependency=log_request_info),
                    )
                )
                _logger.info(f"Registered router from module: {module_name} and dependency {module.dependency}")
        except ModuleNotFoundError as e:
            _logger.info(f"Module not found: {module_name}, error: {e}")
        except AttributeError as e:
            _logger.info(f"Module '{module_name}' does not have 'router' attribute, error: {e}")
        except Exception as e:
            _logger.error(f"Module '{module_name}' failed with the following error: {e}")

    def register_routes(self,app : FastAPI):
        """
            Loop a dir for all python files in addons/ dir, 
            and run include_router_from_module()
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../addons')
        base_module = 'addons'

        for root, dirs, files in os.walk(addons_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    relative_path = os.path.relpath(os.path.join(root, file), addons_dir)
                    module_name = os.path.join(base_module, relative_path).replace(os.sep, '.')[:-3]
                    self.include_router_from_module(app=app, module_name=module_name)