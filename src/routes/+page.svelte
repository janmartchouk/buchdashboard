<script>
	import './style.css';
	import { writable } from "svelte/store";

	// Function to create a writable store that syncs with localStorage (browser-only)
	function createPersistentStore(key, initialValue) {
		// Check if we're in the browser
		if (typeof window !== 'undefined') {
			// Load stored data or use the initial value
			let saved = localStorage.getItem(key);
			let parsed = saved ? JSON.parse(saved) : initialValue;

			// Create writable store
			const store = writable(parsed);

			// Subscribe to changes and update localStorage
			store.subscribe(value => {
				localStorage.setItem(key, JSON.stringify(value));
			});

			return store;
		} else {
			// If not in browser, return an empty store (for SSR environments)
			return writable(initialValue);
		}
	}

	// Persistent store for books
	export const books = createPersistentStore("books", []);

	// Book class
	class Book {
		constructor(title, author, targetprice) {
			this.title = title;
			this.author = author;
			this.links = [];
			this.targetprice = targetprice;
		}
	}

	// Link class
	class Link {
		constructor(url) {
			this.url = url || 'https://';
			this.name = url ? new URL(url).hostname : 'New Link';
			this.price = url ? this.scrapePrice() : 0;
		}
		scrapePrice() {
			// Simulated price scraping
			return 10;
		}
	}

	// Function to add a book
	function addBook() {
		books.update(currentBooks => [...currentBooks, new Book('New Book', 'New Author', 0)]);
	}

	// Function to add a link to a book
	function addLink(book) {
		books.update(currentBooks => {
			return currentBooks.map(b => 
				b === book ? { ...b, links: [...b.links, new Link('')] } : b
			);
		});
	}
</script>

<!-- List of books -->
<div id='book-wrapper'>
	{#each $books as book}
		<div class='book-card'>
			<span class="title-remove-wrapper">
			<input type='text' class='book-title' bind:value={book.title} />
			<button class='remove-book-button' on:click={() => books.update(currentBooks => currentBooks.filter(b => b !== book))}>&times;</button>
			</span>
			<span class='target-price-wrapper'>
				<label for='target-price'>Target:</label>
				<input type='number' class='target-price' name='target-price' bind:value={book.targetprice} />
			</span>
			<ul class="book-links">
				{#each book.links as link}
					<li>
						<input type='text' class='book-link-input' bind:value={link.url} />
						<span class="book-price">{link.price}</span>
						<a class="book-link" href={link.url} target="_blank"> ↗ </a>
					</li>
				{/each}
			</ul>
			<button class='add-link-button' on:click={() => addLink(book)}>Add Link</button>
		</div>
	{/each}
	<button class="add-book-button" on:click={addBook}>Add Book</button>
</div>

