# WineAdvisor Test
Aplicación web basada en Flask diseñada para desplegar las API's REST necesarias para efectuar las acciones CRUD sobre tres modelos de datos (vino, cliente y restaurante) en MongoDB

Credit where credit is due, esta aplicación no habría sido remotamente posible sin el apoyo del [Flask Mega-Tutorial series](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) de Miguel Grinberg

#### Beneficios de usar Flask
- Despacho de solicitudes RESTful.
- Utiliza un motor de plantillas Ninja2.
- Soporte para cookies seguras (sesiones del lado del cliente).
- Amplia documentación.
- Compatibilidad del motor de aplicaciones de Google.
- Las API tienen una forma agradable y son coherentes
- Fácilmente implementable en producción
- Mayor compatibilidad con las últimas tecnologías
- Experimentación técnica
- Más fácil de usar para casos simples
- El tamaño de la base de código es relativamente más pequeño
- Alta escalabilidad para aplicaciones simples,
- Fácil de construir un prototipo rápido
- Enrutar la URL es fácil
- Aplicaciones fáciles de desarrollar y mantener
- La integración de la base de datos es fácil
- Núcleo pequeño y fácilmente extensible
- Plataforma mínima pero potente
- Muchos recursos disponibles en línea, especialmente en GitHub

#### Estructura del Proyecto
- /WineAdvisorTest - Directorio principal. Pero eso ya lo sabían.
    - /app - Contiene toda la magía de back end que se desglozará a continuación
        - /app/__init__.py Aparte de permitir entender a app como un paquete, importamos muchas dependencias y definimos muchas variables de utilidad aquí
        - /app/errors.py A nadie le gustan los errores. Pero cuando llegan, este archivo nos permite tratar con ellos y renderizar páginas personalizadas de error 
        - /app/templates - Las plantillas usadas por Flask para renderizar las páginas web. Todas heredan de base.html gracias a magia de Jira
        - /app/forms.py - Permite definir los formularios usados para ciertas tareas como login, registro, creación de empresas, actualizaión de usuarios, actualización de empresas. Y lo mejor es que si son bien definidos es posible renderizarlos automatizamente gracias a lamagia de WTForms. Pretty nifty stuff
        - /app/models.py Se definen los modelos que queremos usar para la base de datos. Flask tiene una forma un tanto peculiar de lidiar con las relaciones entre modelos. Es mejor entrar con cautela
        - /app/routes.py Aquí pasa casi todo. Modelos y Formularios se unen, así como el enrutamiento y validaciones. 
        - .flaskenv Se definen variables de entorno útiles para Flask que se instancían al correr la aplicación
        - config.py La configuración de la DB se establece aquí
        - handler.py EL núcleo del proyecto. Aunque irónicamente realmente no hace nada de importancia. Pero Flask lo necesita para tener un punto de partida.
        - requirements.txt Archivo que incluye el listado de las dependencias de Python usadas y sus versiones. Debe instalarse de preferencia en un entorno virtual pero hey, no soy nadie para obligarlos
        - tests.py Tests que pueden ser ejecutados directamente por la terminal


### Deployeo local

Lo primero que se debe hacer es clonar el siguente repositorio. Asumiendo que ya está clonado, ingresamos a la carpeta, inicializamos un entorno virtual e instalamos todo lo especificado en requirements
```
$ cd wineadvisortest
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Nota: Si llegan a haber conflictos en la instalación hay que irlos atendiendo conforme vayan surgiendo. En ocasiones es necesario hacer un update y un upgrade a pip pero depende de cada caso.


Una vez configurado eso se puede inicializar la applicaión de flask con el comando 
```
flask run
```

El cuál correrá el servicio y permitirá que desde cualquier navegador se acceda a él por medio de la dirección `http://localhost:5000/`

Una vez se termina de usar el entorno virtual es posible salir usando el comando:
```
(venv) $ deactivate
```



### Flask Docummentation
[Documentación de Flask](https://flask.palletsprojects.com/en/2.0.x/)
