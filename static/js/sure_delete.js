const btnDelete= document.querySelectorAll('.btn-delete')
if(btnDelete){
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) =>{
            if(!confirm('¿Seguro Deseas Borrar Estos Datos?')){
                e.preventDefault();
            }
        });
    });
}


/*
const btnSuccess= document.querySelectorAll('.btn-success')
if(btnSuccess){
    const btnArray = Array.from(btnSuccess);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) =>{
            if(!confirm('¿Seguro Deseas Abonar o Editar?')){
                console.log('¿Seguro Deseas Abonar o Editar?');
                e.preventDefault();
                
            }
        });
    });
}
*/

const boton= document.querySelectorAll('.boton')
if(boton){
    const btnArray = Array.from(boton);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) =>{
            if(!confirm('¿btn?')){
                e.preventDefault();
            }
        });
    });
}
