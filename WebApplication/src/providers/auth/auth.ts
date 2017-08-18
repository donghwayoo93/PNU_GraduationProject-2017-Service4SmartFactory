import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import { Storage } from '@ionic/storage';
import 'rxjs/add/operator/map';

@Injectable()
export class AuthProvider {

  public token: any;

  constructor(public http: Http, public storage: Storage) {
    //console.log('Hello AuthProvider Provider');
  }

  /*
  checkAuthentication() {
    return new Promise((resolve, reject) => {
      //Load token if exists
      this.storage.get('token').then((value) => {
        this.token = value;

        let headers = new Headers();
        headers.append('Authorization', this.token);

        this.http.get('http://localhost:8080/api/auto/protected', { headers: headers })
          .subscribe(res => {
            resolve(res);
          }, (err) => {
            reject(err);
          });
      });
    });
  }
  */

  oldLogin(credentials) {
    return new Promise((resolve, reject) => {
      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      this.http.post('http://localhost:8080/api/auth/login', JSON.stringify(credentials), { headers: headers })
        .subscribe(res => {
          let data = res.json();
          console.log(typeof (data.user))
          console.log(data.user);
          console.log(data.accessLevel);
          this.token = data.token;
          this.storage.set('token', data.token);
          this.storage.set('email', data.user.email)
          this.storage.set('accessLevel', data.user.accessLevel)
          resolve(data);

          resolve(res.json());
        }, (err) => {
          reject(err);
        });
    });
  }

  requestLogin(credentials) {
    return new Promise((resolve, reject) => {
      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      this.http.post('http://localhost:9999/api/requestLogin', JSON.stringify(credentials), { headers: headers })
        .subscribe(res => {
          let data = res.json();
          console.log(data)
          //this.token = data.token;
          //this.storage.set('token', data.token);
          //this.storage.set('email', data.user.email)
          //this.storage.set('accessLevel', data.user.accessLevel)
          resolve(data);

          resolve(res.json());
        }, (err) => {
          reject(err);
        });
    });
  }

  logout() {
    this.storage.set('token', '');
  }

  createAccount(details) {

    return new Promise((resolve, reject) => {

      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      this.http.post('http://localhost:8080/api/auth/register', JSON.stringify(details), { headers: headers })
        .subscribe(res => {

          let data = res.json();
          //this.token = data.token;
          //this.storage.set('token', data.token);
          resolve(data);

        }, (err) => {
          reject(err);
        });

    });

  }
}
