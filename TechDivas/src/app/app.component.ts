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
type Store = "Aldi" | "Coles" | "Woolworths";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"],
})
export class AppComponent {
  missingItemsCount: { [key in Store]: number } = {
    Aldi: 0,
    Coles: 0,
    Woolworths: 0,
  };

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

  cheapestStore: Store | null = null;
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

  get storeKeys(): Store[] {
    return ["Aldi", "Coles", "Woolworths"];
  }

  calculateTotalCosts() {
    this.storeKeys.forEach((store) => {
      // Calculate total cost for each store, ignoring items with zero price.
      this.totalCosts[store] = this.storeBaskets[store]
        .filter((item) => item.price > 0) // Filter out items with zero price
        .reduce((total: number, item: Item) => total + item.price, 0);
    });
  }

  clearSearch() {
    this.inputItemList = [];
    this.outputItemList = [];
    this.storeBaskets = {
      Aldi: [],
      Coles: [],
      Woolworths: [],
    };
    this.missingItemsCount = {
      Aldi: 0,
      Coles: 0,
      Woolworths: 0,
    };
    this.totalCosts = {
      Aldi: 0,
      Coles: 0,
      Woolworths: 0,
    };
    this.cheapestStore = null;
    this.submissionMessage = "";
    this.errorMessage = "";
    this.isSearchSubmitted = false;
    this.item = "";
    this.quantity = 0;
    this.itemType = null;
    this.isQuantityInputDisabled = true;
  }

  getCheapestStore(): Store | null {
    // Filter out stores with a total cost of 0
    const validStores = this.storeKeys.filter(
      (store) => this.totalCosts[store] > 0
    );

    if (validStores.length === 0) {
      return null;
    }

    // Find the store with the minimum total cost
    return validStores.reduce((cheapest, store) => {
      return this.totalCosts[store] < this.totalCosts[cheapest]
        ? store
        : cheapest;
    }, validStores[0]);
  }
  fetchBaskets(): void {
    const basketData = this.inputItemList.map((item) => ({ name: item.name }));
    if (basketData.length > 0) {
      this.apiservice.getStoreBaskets(basketData).subscribe({
        next: (response) => {
          this.storeBaskets = { Aldi: [], Coles: [], Woolworths: [] }; // Reset baskets
          this.missingItemsCount = { Aldi: 0, Coles: 0, Woolworths: 0 }; // Reset missing items count

          this.inputItemList.forEach((item) => {
            ["Aldi", "Coles", "Woolworths"].forEach((store) => {
              const storeBasket = response[`${store.toLowerCase()}Basket`];
              const storeItems = storeBasket ? storeBasket[store] : [];

              if (storeItems && storeItems.length > 0) {
                const storeItem = storeItems.find(
                  (sItem: Item) =>
                    sItem.name.toLowerCase() === item.name.toLowerCase()
                );
                if (storeItem) {
                  // Capitalize store item name before adding
                  this.storeBaskets[store].push({
                    ...storeItem,
                    name: this.capitalizeWords(storeItem.name), // Capitalize the name
                  });
                } else {
                  // Increment the missing item count directly
                  this.missingItemsCount[store as Store]++;

                  // Add missing item to the store basket with capitalized name
                  this.storeBaskets[store].push({
                    name: this.capitalizeWords(item.name), // Capitalize the name
                    store,
                    price: 0,
                    quantity: "Not Found",
                  });
                }
              } else {
                // Increment count if no data at all for this store
                this.missingItemsCount[store as Store]++;

                // Add missing item to the store basket with capitalized name
                this.storeBaskets[store].push({
                  name: this.capitalizeWords(item.name), // Capitalize the name
                  store,
                  price: 0,
                  quantity: "Not Found",
                });
              }
            });
          });

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

  getMissingCountForStore(store: Store): number {
    console.log(store);
    console.log(this.missingItemsCount[store]);

    return this.missingItemsCount[store];
  }
  checkItem() {
    const lowerCaseItem = this.item.toLowerCase();
    const items: { [key: string]: string } = {
      milk: "litres",
      bread: "slices",
      apple: "units",
      chicken: "kilograms",
      noodle: "grams",
      dumplings: "units",
      pastaSauce: "grams",
      laundryLiquid: "litres",
      lasagne: "grams",
      sausages: "units",
      steak: "grams",
      lamb: "kilograms",
      bacon: "grams",
      kiwifruit: "units",
      celery: "stalks",
      broccoli: "heads",
      onions: "units",
      carrots: "units",
      beans: "grams",
    };
    if (items[lowerCaseItem]) {
      this.itemType = items[lowerCaseItem];
      this.isQuantityInputDisabled = false;
    } else {
      this.itemType = "Item not found";
      this.isQuantityInputDisabled = true;
    }
  }
  itemNotFound(itemName: string, store: string): boolean {
    return !this.storeBaskets[store].some(
      (sItem) => sItem.name.toLowerCase() === itemName.toLowerCase()
    );
  }

  addItem() {
    if (this.item && this.itemType && this.quantity > 0) {
      this.inputItemList.push({
        name: this.capitalizeWords(this.item),
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
  private capitalizeWords(string: string): string {
    return string
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ");
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
                name: this.capitalizeWords(productName),
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
