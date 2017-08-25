import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { AuthProvider } from '../auth/auth'
import 'rxjs/add/operator/map';

@Injectable()
export class MachinesProvider {

  constructor(public http: Http, public authService: AuthProvider) {
    //console.log('Hello MachinesProvider Provider');
  }

  getMachineInformation(credentials) {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/machines/info', JSON.stringify(credentials))
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

  getMachineSensorData(credentials) {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/machines/sensor', JSON.stringify(credentials))
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }

  getMachineManual(credentials) {
    return new Promise((resolve, reject) => {
      this.http.get('http://localhost:9999/api/machines/manual', JSON.stringify(credentials))
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }
}
