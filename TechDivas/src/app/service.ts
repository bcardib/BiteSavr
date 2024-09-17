import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Item {
  name: string;
  shop: string;
  price: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiserviceService {
  private apiUrl = 'http://127.0.0.1:5000/api'; 

  constructor(private http: HttpClient) {}

  getData(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/data`);
  }

  getItems(): Observable<Item[]> {
    return this.http.get<Item[]>(`${this.apiUrl}/items`);
  }

  submitData(itemList: any[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/submit`, itemList);
  }
}
