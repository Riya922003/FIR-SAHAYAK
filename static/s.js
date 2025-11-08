var login_page = document.querySelector(".login_page");
var signup_page = document.querySelector(".signup_page");

var signup = document.querySelector(".signup");
var signin = document.querySelector(".signin");

var card_toggle=document.querySelector(".card");

if (login_page) {
    login_page.onclick = function(){
        if (signup) signup.classList.toggle('hidden');
        if (signin) signin.classList.toggle('hidden');
        // if (card_toggle) card_toggle.classList.toggle('active'); 
    }
}

if (signup_page) {
    signup_page.onclick = function(){
        if (signup) signup.classList.toggle('hidden');
        if (signin) signin.classList.toggle('hidden');
    }
}

var signup_eye = document.querySelector(".signup_eye");
var signup_pass = document.querySelector(".signup_pass");
var set_signup_eye = document.querySelector(".signup_eye");
if (signup_eye) {
    signup_eye.onclick = function(){
        if (signup_pass && signup_pass.type=="password"){
            signup_pass.type="text";
            if (set_signup_eye) { set_signup_eye.classList.remove('fa-eye-slash'); set_signup_eye.classList.add('fa-eye'); }
        }
        else if (signup_pass){
            signup_pass.type="password";
            if (set_signup_eye) { set_signup_eye.classList.add('fa-eye-slash'); set_signup_eye.classList.remove('fa-eye'); }
        }
    }
}

var login_eye = document.querySelector(".login_eye");
var login_pass = document.querySelector(".login_pass");
var set_login_eye = document.querySelector(".login_eye");
if (login_eye) {
    login_eye.onclick = function(){
        if (login_pass && login_pass.type=="password"){
            login_pass.type="text";
            if (set_login_eye) { set_login_eye.classList.remove('fa-eye-slash'); set_login_eye.classList.add('fa-eye'); }
        }
        else if (login_pass){
            login_pass.type="password";
            if (set_login_eye) { set_login_eye.classList.add('fa-eye-slash'); set_login_eye.classList.remove('fa-eye'); }
        }
    }
}

var click_signup = document.querySelector(".click_signup");
if (click_signup) click_signup.addEventListener('click',function(){
    click_signup.classList.toggle('signup_bg');
});

var click_login = document.querySelector(".click_login");
if (click_login) click_login.addEventListener('click',function(){
    click_login.classList.toggle('signup_bg');
});




var signup_inputs=document.querySelectorAll(".signup input");
var signup_btn=document.querySelector(".signup_btn");
var i=1;

if (signup_btn) signup_btn.addEventListener('click',function(){
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
            if(i>2){ i=0; }    
            if (signup_inputs[i]) signup_inputs[i].focus();        
            i++;
        }   
        if(inpts.value.length<1){ inpts.classList.add('warning'); } 
        else{ inpts.classList.remove('warning'); } 
    });
}); 

var signin_inputs=document.querySelectorAll(".signin input");
var signin_btn=document.querySelector(".signin_btn"); 
if (signin_btn) signin_btn.addEventListener('click',function(){ 
    signin_inputs.forEach((inpts)=>{
        inpts.classList.remove('warning');
        if(inpts.value.length<1){ inpts.classList.add('warning'); return false; }
    }); 
}); 
signin_inputs.forEach((inpts)=>{
    inpts.addEventListener('keyup',function(){
        if(inpts.value.length<1){ inpts.classList.add('warning'); } 
        else{ inpts.classList.remove('warning'); } 
    }); 
}); 