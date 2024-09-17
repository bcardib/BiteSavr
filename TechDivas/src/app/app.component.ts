import { Component, OnInit } from '@angular/core';
import { ApiserviceService } from './service';
import { FormsModule } from '@angular/forms'; 
import { CommonModule } from '@angular/common'; 

interface Item {
  name: string;
  shop: string;
  price: number; 
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule], 
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  newdata: any;
  title: string = '';
  message: string = '';
  
  itemType: string | null = null;
  item: string = ''; 
  quantity: number = 0;
  isQuantityInputDisabled = true;

  items: { [key: string]: string } = {
    milk: 'Dairy',
    bread: 'Grain',
    apple: 'Fruit',
    chicken: 'Meat'
  };

  itemList: { item: string, type: string, quantity: number, price: number }[] = []; 
  itemsList: Item[] = [];
  sortedItems: { [shop: string]: Item[] } = {}; 

  constructor(private apiservice: ApiserviceService) {}

  ngOnInit() {
    this.getData();
    this.getItems();
  }

  checkItem() {
    const lowerCaseItem = this.item.toLowerCase();
    if (this.items[lowerCaseItem]) {
      this.itemType = this.items[lowerCaseItem];
      this.isQuantityInputDisabled = false; 
    } else {
      this.itemType = 'Item not found';
      this.isQuantityInputDisabled = true; 
    }
  }

  addItem() {
    if (this.item && this.itemType && this.quantity > 0) {
      const foundItem = this.itemsList.find(i => i.name.toLowerCase() === this.item.toLowerCase());
      const price = foundItem ? foundItem.price : 0;

      this.itemList.push({ item: this.item, type: this.itemType, quantity: this.quantity, price });
      this.item = '';
      this.quantity = 0;
      this.itemType = null;
      this.isQuantityInputDisabled = true;
    } else {
      alert('Please provide valid item and quantity.');
    }
  }

  submitData() {
    this.apiservice.submitData(this.itemList).subscribe(
      response => {
        console.log('Data successfully submitted:', response);
        this.itemList = [];
      },
      error => {
        console.error('Error submitting data:', error);
      }
    );
  }

  getData() {
    this.apiservice.getData().subscribe(res => {
      this.newdata = res;
      this.title = this.newdata.title;
      this.message = this.newdata.message;
    });
  }

  getItems() {
    this.apiservice.getItems().subscribe(
      items => {
        this.itemsList = items;
        this.groupItemsByShop();
      },
      error => {
        console.error('Error fetching items:', error);
      }
    );
  }

  groupItemsByShop() {
    this.sortedItems = this.itemsList.reduce((acc: { [shop: string]: Item[] }, item: Item) => {
      if (!acc[item.shop]) {
        acc[item.shop] = [];
      }
      acc[item.shop].push(item);
      return acc;
    }, {});
  }
}
