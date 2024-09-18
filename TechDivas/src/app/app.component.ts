import { Component, OnInit } from "@angular/core";
import { ApiserviceService } from "./service";
import { FormsModule } from "@angular/forms";
import { CommonModule } from "@angular/common";
import { ChangeDetectorRef } from "@angular/core";

interface Item {
  name: string;
  store: string;
  price: number;
  quantity: string;
}

@Component({
  selector: "app-root",
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"],
})
export class AppComponent {
  isSecondPage = false;
  isSearchSubmitted = false;
  expanded = false;
  item: string = "";
  quantity: number = 0;
  isQuantityInputDisabled = true;
  itemType: string | null = null;
  inputItemList: { name: string; type: string; quantity: number }[] = [];
  outputItemList: {
    name: string;
    store: string;
    price: number;
    quantity: string;
  }[] = [];
  storeCheapest: { [store: string]: any[] } = {};
  totalCosts: { [store: string]: number } = {
    Aldi: 0,
    Coles: 0,
    Woolworths: 0,
  };
  cheapestStore: string = "";
  submissionMessage: string = "";
  errorMessage: string = "";
  storeBaskets: { [store: string]: Item[] } = {
    Aldi: [],
    Coles: [],
    Woolworths: [],
  };
  itemsList: Item[] = [];
  sortedItems: { [store: string]: Item[] } = {};
  basket = [{ name: "Milk" }, { name: "Bread" }, { name: "Apple" }];

  constructor(
    private apiservice: ApiserviceService,
    private cdr: ChangeDetectorRef
  ) {}

  togglePage() {
    if (this.isSearchSubmitted) {
      this.isSecondPage = !this.isSecondPage;
    }
  }

  toggleExpanded() {
    this.expanded = !this.expanded;
  }

  get storeKeys(): string[] {
    return Object.keys(this.storeBaskets);
  }

  calculateTotalCosts() {
    this.storeKeys.forEach((store) => {
      this.totalCosts[store] = this.storeBaskets[store].reduce(
        (total: number, item: Item) => total + item.price,
        0
      );
    });
  }

  getCheapestStore(): string {
    return this.storeKeys.reduce((cheapest, store) => {
      return this.totalCosts[store] < this.totalCosts[cheapest]
        ? store
        : cheapest;
    }, this.storeKeys[0]);
  }
  fetchBaskets(): void {
    const basketData = this.inputItemList.map((item) => ({ name: item.name }));
    if (basketData.length > 0) {
      this.apiservice.getStoreBaskets(basketData).subscribe({
        next: (response) => {
          if (response.aldiBasket && Array.isArray(response.aldiBasket.Aldi)) {
            this.storeBaskets["Aldi"] = response.aldiBasket.Aldi;
          }
          if (
            response.colesBasket &&
            Array.isArray(response.colesBasket.Coles)
          ) {
            this.storeBaskets["Coles"] = response.colesBasket.Coles;
          }
          if (
            response.woolworthsBasket &&
            Array.isArray(response.woolworthsBasket.Woolworths)
          ) {
            this.storeBaskets["Woolworths"] =
              response.woolworthsBasket.Woolworths;
          }
          this.calculateTotalCosts();
          this.cheapestStore = this.getCheapestStore();
        },
        error: (error) => {
          console.error("Error fetching store baskets:", error);
        },
        complete: () => {
          console.log("Store basket fetch completed");
        },
      });
      this.cdr.detectChanges();
    }
  }

  checkItem() {
    const lowerCaseItem = this.item.toLowerCase();
    const items: { [key: string]: string } = {
      milk: "litres",
      bread: "Grain",
      apple: "Fruit",
      chicken: "Meat",
    };

    if (items[lowerCaseItem]) {
      this.itemType = items[lowerCaseItem];
      this.isQuantityInputDisabled = false;
    } else {
      this.itemType = "Item not found";
      this.isQuantityInputDisabled = true;
    }
  }

  addItem() {
    if (this.item && this.itemType && this.quantity > 0) {
      this.inputItemList.push({
        name: this.item,
        type: this.itemType,
        quantity: this.quantity,
      });
      this.item = "";
      this.quantity = 0;
      this.itemType = null;
      this.isQuantityInputDisabled = true;
    } else {
      alert("Please provide valid item and quantity.");
    }
  }

  submitData() {
    this.apiservice.submitData(this.inputItemList).subscribe(
      (response: any) => {
        if (response && response.cheapestProducts) {
          this.outputItemList = [];
          for (const productName in response.cheapestProducts) {
            if (response.cheapestProducts.hasOwnProperty(productName)) {
              const product = response.cheapestProducts[productName];
              this.outputItemList.push({
                name: productName,
                store: product.store,
                price: product.price,
                quantity: product.quantity,
              });
            }
          }
          this.storeCheapest = response.cheapestProducts;
          this.totalCosts = response.totalCosts;
          this.cheapestStore = response.cheapestStore;
          this.submissionMessage =
            "Data submitted and output list updated successfully!";
          this.errorMessage = "";
          this.isSearchSubmitted = true;
          this.fetchBaskets();
        } else {
          this.submissionMessage = "";
          this.errorMessage = "No products found in response.";
        }
      },
      (error) => {
        console.error("Error submitting data:", error);
        this.errorMessage = "An error occurred while submitting data.";
        this.submissionMessage = "";
      }
    );
  }
}
