import { Component } from '@angular/core';
import { NavController, LoadingController, ToastController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';

import { MenuPage } from '../menu/menu';
import { SignupPage } from '../signup/signup';

import { MachinesProvider } from '../../providers/machines/machines';
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
    public ConnectionService: ConnectionProvider, public storage: Storage,
    private machineService: MachinesProvider, private alertCtrl: AlertController) {
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
      this.storage.get('accessLevel').then(userAccessLevel => {

        this.machineService.getMachineInformation(credentials).then((result) => {
          this.loading.dismiss();
          var machineAccessLevel = result[0].accessLevel;
          if (userAccessLevel <= machineAccessLevel) {//숫자가 높으면 낮은 보안등급
            // 가능
            this.navCtrl.setRoot(MenuPage);
          } else {
            //불가능
            this.showSecurityAlert();
          }
        }, (err) => {
          this.loading.dismiss();
          console.log(err);
        });
        this.loading.dismiss();
      });
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
      });
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
      });
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

  showSecurityAlert() {
    let alert = this.alertCtrl.create({
      title: "Security Alert",
      message: "you have lower Access level.",
      buttons: ['OK']
    });
    alert.present();
  }
}
