import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class ApiserviceService {
  private apiUrl = "http://127.0.0.1:5000/api";

  constructor(private http: HttpClient) {}

  submitData(itemList: any[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/submit`, itemList);
  }

  getData(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/data`);
  }

  getItems(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/items`);
  }



  getStoreBaskets(basket: any[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/store_baskets`, { basket });
  }
}
