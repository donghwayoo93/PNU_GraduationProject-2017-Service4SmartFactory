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

  requestLogin(credentials) {
    return new Promise((resolve, reject) => {
      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      this.http.post('http://localhost:9999/api/requestLogin', JSON.stringify(credentials), { headers: headers })
        .subscribe(res => {
          let data = res.json();
          //console.log(data)
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

  logout() {
    this.storage.set('token', '');
    this.storage.set('email', '');
    this.storage.set('accessLevel', '');
  }

  createAccount(details) {

    return new Promise((resolve, reject) => {

      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      this.http.post('http://localhost:8088/api/auth/register', JSON.stringify(details), { headers: headers })
        .subscribe(res => {

          let data = res.json();
          this.token = data.token;
          this.storage.set('token', data.token);
          resolve(data);

        }, (err) => {
          reject(err);
        });

    });

  }
}
