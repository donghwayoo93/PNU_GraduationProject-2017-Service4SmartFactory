import { Component } from '@angular/core';
import { NavController, LoadingController } from 'ionic-angular';

import { MenuPage } from '../menu/menu';
import { SignupPage } from '../signup/signup'

import { AuthProvider } from '../../providers/auth/auth'

@Component({
  selector: 'page-login',
  templateUrl: 'login.html',
})
export class LoginPage {

  email: string;
  password: string;
  loading: any;

  constructor(public navCtrl: NavController, public authService: AuthProvider, public loadingCtrl: LoadingController) {
  }

  ionViewDidLoad() {
    this.showLoader();

    //Check if already authenticated
    this.authService.checkAuthentication().then((res) => {
      console.log("Already authorized");
      this.loading.dismiss();
      this.navCtrl.setRoot(MenuPage);
    }, (err) => {
      console.log("Not already authorized");
      this.loading.dismiss();
    });
  }

  login(){
    this.showLoader();
    let credentials = {
      email: this.email,
      password: this.password
    };
    
    this.authService.login(credentials).then((result) => {
      this.loading.dismiss();
      console.log(result);
      this.navCtrl.setRoot(MenuPage);
    }, (err) => {
      this.loading.dismiss();
      console.log(err);
    });
  }

  launchSignup(){
      this.navCtrl.push(SignupPage);
  }
 

  showLoader(){
    this.loading = this.loadingCtrl.create({
      content: 'Authentication...'
    });

    this.loading.present();
  }
}
