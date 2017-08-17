import { Component } from '@angular/core';
import { NavController, LoadingController } from 'ionic-angular';
import { AuthProvider } from '../../providers/auth/auth'
import { MenuPage } from '../menu/menu'

@Component({
  selector: 'page-signup',
  templateUrl: 'signup.html',
})
export class SignupPage {
  email: string;
  password: string;
  accessLevel: string;
  loading: any;

  constructor(public navCtrl: NavController, public authService: AuthProvider, public loadingCtrl: LoadingController) {
 
  }
 
  register(){
 
    this.showLoader();
 
    let details = {
        email: this.email,
        password: this.password,
        accessLevel: this.accessLevel
    };
 
    this.authService.createAccount(details).then((result) => {
      this.loading.dismiss();
      console.log(result);
      this.navCtrl.setRoot(MenuPage);
    }, (err) => {
        this.loading.dismiss();
    });
 
  }
 
  showLoader(){
 
    this.loading = this.loadingCtrl.create({
      content: 'Authenticating...'
    });
 
    this.loading.present();
 
  }

}
