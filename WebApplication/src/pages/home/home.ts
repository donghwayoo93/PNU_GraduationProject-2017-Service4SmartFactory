import { Component } from '@angular/core';
import { NavController, AlertController,LoadingController, ModalController, MenuController } from 'ionic-angular';
import { TodosProvider } from '../../providers/todos/todos'
import { AuthProvider } from '../../providers/auth/auth'
import { LoginPage } from '../login/login'

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {
  todos: any;
  loading: any;
  activeMenu: string;
 
  constructor(public navCtrl: NavController, public todoService: TodosProvider, public modalCtrl: ModalController, 
    public alertCtrl: AlertController, public authService: AuthProvider, public loadingCtrl: LoadingController,
    public menu: MenuController) {

  }
 
  ionViewDidLoad(){
 
    this.todoService.getTodos().then((data) => {
          this.todos = data;
    }, (err) => {
        console.log("not allowed");
    });
 
  }
 
  addTodo(){
 
    let prompt = this.alertCtrl.create({
      title: 'Add Todo',
      message: 'Describe your todo below:',
      inputs: [
        {
          name: 'title'
        }
      ],
      buttons: [
        {
          text: 'Cancel'
        },
        {
          text: 'Save',
          handler: todo => {
 
                if(todo){
 
                    this.showLoader();
 
                    this.todoService.createTodo(todo).then((result) => {
                        this.loading.dismiss();
                        this.todos = result;
                        console.log("todo created");
                    }, (err) => {
                        this.loading.dismiss();
                        console.log("not allowed");
                    });
 
                }
 
 
          }
        }
      ]
    });
 
    prompt.present();
 
  }
 
  deleteTodo(todo){
 
    this.showLoader();
 
    //Remove from database
    this.todoService.deleteTodo(todo._id).then((result) => {
 
      this.loading.dismiss();
 
      //Remove locally
        let index = this.todos.indexOf(todo);
 
        if(index > -1){
            this.todos.splice(index, 1);
        }   
 
    }, (err) => {
      this.loading.dismiss();
        console.log("not allowed");
    });
  }
 
  menuActive(){
    this.activeMenu = 'menu1';
  }
  showLoader(){
 
    this.loading = this.loadingCtrl.create({
      content: 'Authenticating...'
    });
 
    this.loading.present();
 
  }
 
  logout(){
 
    this.authService.logout();
    this.navCtrl.setRoot(LoginPage);
 
  }

}
