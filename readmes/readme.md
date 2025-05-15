# Ejercicio 1: Reflected XSS

Añadimos un campo en la página web con jinja que introduce en el html el valor de un parámetro de la URL, sin sanitizar la entrada

Código original:
```html
<div class="row mt-5 mb-5">
    <div class="col">
        <p class="svaia-text mb-0" style="font-size: 8rem;">SVAIA</p>
        <p class="text-dark fs-4"><i>Sistema de soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial</i></p>
    </div>
</div>
```

Código inseguro:
```html
<div class="row mt-5 mb-5">
    <div class="col">
        <p class="svaia-text mb-0" style="font-size: 8rem;">SVAIA</p>
        <p class="text-dark fs-4"><i>Sistema de soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial</i></p>
        {% if request.args.get('xss') %}
            <p>{{ request.args.get('xss') | safe }}</p>
        {% endif %}
    </div>
</div>
```

Como se ve sin argumentos en la URL:
![ej01_normal](ej01_normal.png)

Inyectando código html en el argumento:
![ej01_inyeccion_html](ej01_inyeccion_html.png)

Inyectando código javascript en el argumento de la URL para mostrar una alerta:
![ej01_alerta](ej01_alerta.png)

# Ejercicio 2: Stored XSS

Hacemos que al cargar un proyecto en la página de admin, en vez de introducir la descripción en un campo de texto, sustituimos el innerHTML del elemento

Version segura:
```js
projectItem.querySelector('.project-description').textContent = `Descripción: ${project.description}`;
```

Versión insegura:
```js
projectItem.querySelector('.project-description').innerHTML = `Descripción: ${project.description}`;
```

Cómo se ve de normal:
![ej02_normal](ej02_normal.png)

Un usuario del sistema introduce el siguiente payload en la descripción.

```html
<img src="x" onerror="alert(`hola`)">
```

Cuando se carga el proyecto desde la página de admin, se ejecuta el código javascript, intentando cargar una imagen desde la URL, que no existe, por lo que se ejecuta el código javascript y se muestra una alerta:
![ej02_alerta](ej02_alerta.png)

# Ejercicio 3: DOM-based XSS

Añadimos el siguiente código en el archivo projects.js. Esto lo que hace es cambiar el nombre del proyecto en función del parámetro que se le pasa como argumento en la URL.

Código original:
```js
projectItem.querySelector('.project-name').textContent = `Nombre: ${project.name}`;
```

Código inseguro:
```js
const urlParams = new URLSearchParams(window.location.search);
const name = urlParams.get('name');
if (name) {
    projectItem.querySelector('.project-name').innerHTML = `Nombre: ${name}`;
}
else {
    projectItem.querySelector('.project-name').textContent = `Nombre: ${project.name}`;
}
```

Cómo se ve de normal:
![ej03_normal](ej03_normal.png)

Inyectando un payload de JavaScript en el argumento de la URL:

```js
<img src="x" onerror="alert(`hola`)">
``` 

![ej03_js](ej03_alert.png)
