import { Component,ViewChild } from '@angular/core';
import { Nav, NavController, NavParams } from 'ionic-angular';

import { ControlMachinePage } from '../control-machine/control-machine';
import { LoginPage } from '../login/login'

import { AuthProvider } from '../../providers/auth/auth'

@Component({
  selector: 'page-menu',
  templateUrl: 'menu.html',
})
export class MenuPage {
  @ViewChild(Nav) nav: Nav;

  user: string;
  rootPage: any = ControlMachinePage;

  pages: Array<{title: string, component: any}>;

  constructor(public navCtrl: NavController, public navParams: NavParams,
  public authService: AuthProvider) {// used for an example of ngFor and navigation
    this.pages = [
      { title: '관제', component: ControlMachinePage }
    ];
    this.user = this.getUser();
    console.log(localStorage.getItem('email'))
  }

  openPage(page) {
    // Reset the content nav to have just this page
    // we wouldn't want the back button to show in this scenario
    this.nav.setRoot(page.component);
  }

  logout() {
    this.authService.logout();
    this.navCtrl.setRoot(LoginPage);

  }

  getUser() {
    return JSON.parse(localStorage.getItem('email'))
  }
  getAccessLevel() {
    return JSON.parse(localStorage.getItem('accessLevel'))
  }
}
