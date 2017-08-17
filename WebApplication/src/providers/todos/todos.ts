import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import { AuthProvider } from '../auth/auth'
import 'rxjs/add/operator/map';

@Injectable()
export class TodosProvider {

  constructor(public http: Http, public authService: AuthProvider) {
    console.log('Hello TodosProvider Provider');
  }

  getTodos() {
    return new Promise((resolve, reject) => {
      let headers = new Headers();
      headers.append('Authorization', this.authService.token);
      this.http.get('http://localhost:8080/api/todos', { headers: headers })
        .map(res => res.json())
        .subscribe(data => {
          resolve(data);
        }, (err) => {
          reject(err);
        });
    });
  }
  createTodo(todo) {
    return new Promise((resolve, reject) => {

      let headers = new Headers();
      headers.append('Content-Type', 'application/json');
      headers.append('Authorization', this.authService.token);

      this.http.post('http://localhost:8080/api/todos', JSON.stringify(todo), { headers: headers })
        .map(res => res.json())
        .subscribe(res => {
          resolve(res);
        }, (err) => {
          reject(err);
        });

    });

  }

  deleteTodo(id) {

    return new Promise((resolve, reject) => {

      let headers = new Headers();
      headers.append('Authorization', this.authService.token);

      this.http.delete('http://localhost:8080/api/todos/' + id, { headers: headers }).subscribe((res) => {
        resolve(res);
      }, (err) => {
        reject(err);
      });

    });

  }

}