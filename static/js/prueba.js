
//const fs = requiere ('fs');

//let data=fs.readFileSync('./src/pruebajs.js');
//const jsonData=JSON.parse(datosgrafico.json)
//console.log(jsonData);


  // console.log(fetch('datosgrafico.json'))

  // fetch('datosgrafico.json').then(respuesta => respuesta.json()).then(respuesta => console.log(respuesta))
var arradata=new Array();
var a=new Array();
var archivoTxt= new XMLHttpRequest();
var fileRuta='static/js/datosgrafico.json'
//var fileRuta='src/pruebajs.json'
archivoTxt.open("GET",fileRuta,false);
archivoTxt.send(null);
var txt = archivoTxt.responseText;
for(var i=0;i<txt.length;i++){
    arradata.push(txt[i]);
}
//console.log("antes de fetch");
//a=fetch('static/js/datosgrafico.json').then(respuesta => respuesta.json()).then(respuesta => console.log(respuesta));
//a=fetch(txt).then(respuesta => respuesta.json()).then(respuesta => console.log(respuesta));
//console.log("despues de fetch");
//arradata.then(respuesta => respuesta.json()).then(respuesta => console.log(respuesta));

/*
arradata.forEach(function(data){
    console.log(data);
});
*/

//console.log(txt);
//console.log("a = "+a )
var b = JSON.parse(txt)
console.log(txt)
console.log(b)
console.log("for")
console.log(b.length)
for(var e=0;e<b.length;e++){
  console.log(b[e].rojo);
}
console.log("despues del for")
console.log(b[0].rojo);
var res = document.querySelectorAll('res');
//res.innerHTML='';
res.innerHTML = '</td>${b[0].rojo}</tr>'

