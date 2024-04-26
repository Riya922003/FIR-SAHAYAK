var login_page = document.querySelector(".login_page");
var signup_page = document.querySelector(".signup_page");

var signup = document.querySelector(".signup");
var signin = document.querySelector(".signin");

var card_toggle=document.querySelector(".card");

login_page.onclick=function(){
signup.classList.toggle('hidden');
signin.classList.toggle('hidden');
// card_toggle.classList.toggle('active'); 
}

signup_page.onclick=function(){
signup.classList.toggle('hidden');
signin.classList.toggle('hidden');
}

var signup_eye = document.querySelector(".signup_eye");
var signup_pass = document.querySelector(".signup_pass");
var set_signup_eye = document.querySelector(".signup_eye");

signup_eye.onclick=function(){
if(signup_pass.type=="password"){
signup_pass.type="text";
set_signup_eye.classList.remove('fa-eye-slash');
set_signup_eye.classList.add('fa-eye');
}
else{
signup_pass.type="password";
set_signup_eye.classList.add('fa-eye-slash');
set_signup_eye.classList.remove('fa-eye');
}
}

var login_eye = document.querySelector(".login_eye");
var login_pass = document.querySelector(".login_pass");
var set_login_eye = document.querySelector(".login_eye");

login_eye.onclick=function(){
if(login_pass.type=="password"){
login_pass.type="text";
set_login_eye.classList.remove('fa-eye-slash');
set_login_eye.classList.add('fa-eye');
}
else{
login_pass.type="password";
set_login_eye.classList.add('fa-eye-slash');
set_login_eye.classList.remove('fa-eye');
}
}

var click_signup = document.querySelector(".click_signup");
click_signup.addEventListener('click',function(){
click_signup.classList.toggle('signup_bg');
});

var click_login = document.querySelector(".click_login");
click_login.addEventListener('click',function(){
click_login.classList.toggle('signup_bg');
});




var signup_inputs=document.querySelectorAll(".signup input");
var signup_btn=document.querySelector(".signup_btn");
var i=1;


signup_btn.addEventListener('click',function(){
signup_inputs.forEach((inpts)=>{
inpts.classList.remove('warning');
if(inpts.value.length<1){ 
    inpts.classList.add('warning'); 
    } 
    }); 
    }); 
    
var enter=0; 
signup_inputs.forEach((inpts)=>{
    inpts.addEventListener('keyup',function(event){
    if(event.key==="Enter"){
        
    if(i>2){
        i=0;
    }    
   
    signup_inputs[i].focus();        
    i++;
    }   
    
    if(inpts.value.length<1){ 
        inpts.classList.add('warning'); 
        
    } 
    else{
        inpts.classList.remove('warning');
        } 
        
    });
    }); 
    
    
    var signin_inputs=document.querySelectorAll(".signin input");
    var signin_btn=document.querySelector(".signin_btn"); 
    signin_btn.addEventListener('click',function(){ 
        signin_inputs.forEach((inpts)=>{
        inpts.classList.remove('warning');
        
        if(inpts.value.length<1){ 
            inpts.classList.add('warning'); 
            return false;
            }
            }); 
        
    }); 
    signin_inputs.forEach((inpts)=>{
            inpts.addEventListener('keyup',function(){
            if(inpts.value.length<1){ 
                inpts.classList.add('warning');
                } 
                else{ 
                    inpts.classList.remove('warning'); 
                    
                } 
                
            }); 
        
    });