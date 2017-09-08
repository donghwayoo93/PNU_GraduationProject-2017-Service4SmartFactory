import { Component } from '@angular/core';
import { NavController, LoadingController, ToastController } from 'ionic-angular';

import { MenuPage } from '../menu/menu';
import { SignupPage } from '../signup/signup';

import { AuthProvider } from '../../providers/auth/auth';
import { ConnectionProvider } from '../../providers/connection/connection';

@Component({
  selector: 'page-login',
  templateUrl: 'login.html',
})
export class LoginPage {

  email: string;
  password: string;
  loading: any;
  toggleStatus: boolean;
  connectionStatus: boolean;

  constructor(public navCtrl: NavController, public authService: AuthProvider,
    public loadingCtrl: LoadingController, public toastCtrl: ToastController,
    public ConnectionService: ConnectionProvider) {
  }

  ionViewDidLoad() {
    this.toggleStatus = false;
    this.connectionStatus = false;
  }

  login() {
    this.showLoader("Authentication...");
    let credentials = {
      email: this.email,
      password: this.password
    };

    this.authService.requestLogin(credentials).then((result) => {
      this.loading.dismiss();
      //console.log(result);
      this.navCtrl.setRoot(MenuPage);
    }, (err) => {
      this.loading.dismiss();
      this.presentToast("Failed to Sign in");
    });
  }

  updateConnection() {
    if (this.toggleStatus == true) {
      this.showLoader("Connecting...");
      this.ConnectionService.tryConnect().then((result) => {
        console.log(result[0]);
        if (result[0] == "TRUE") {
          this.presentToast("Success connecting");
          this.loading.dismiss();
          this.connectionStatus = true;
        }
      }, (err) => {
        this.presentToast("Failed to connect");
        this.toggleStatus = false;
        this.loading.dismiss();
      })
    } else {
      this.showLoader("disconnect...");
      this.ConnectionService.tryDisconnect().then((result) => {
        console.log(result[0]);
        if (result[0] == "TRUE") {
          this.presentToast("Success disconnecting");
          this.loading.dismiss();
          this.connectionStatus = false;
        }
      }, (err) => {
        this.presentToast("Failed to disconnect");
        this.toggleStatus = true;
        this.loading.dismiss();
      })
    }
  }

  showLoader(content) {
    this.loading = this.loadingCtrl.create({
      content: content
    });
    this.loading.present();
  }

  launchSignup() {
    this.navCtrl.push(SignupPage);
  }

  presentToast(message) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 1500,
      position: 'top'
    });
    toast.present();
  }


}
