# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Get last 5 items from Facebook Marketplace added in the last 24 hours.

Requires specifying a user_data_dir for a browser that is logged in to Facebook.

Usage:
python facebook_marketplace.py <user_data_dir> [--search_item <item_name>] [--headless]
"""

import fire  # type: ignore
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from pyfzf.pyfzf import FzfPrompt

from nova_act import NovaAct

load_dotenv()


class MarketplaceItem(BaseModel):
    title: str
    price: str
    location: str
    time_posted: str


class MarketplaceItems(BaseModel):
    items: List[MarketplaceItem]


def main(user_data_dir: str = None, headless: bool = None, search_item: str = "screens") -> None:
    # Use environment variable if user_data_dir not provided
    if user_data_dir is None:
        user_data_dir = os.getenv('USER_DATA_DIR')
        if user_data_dir is None:
            raise ValueError("USER_DATA_DIR must be provided either as parameter or in .env file")
    
    # Interactive headless mode selection if not specified
    if headless is None:
        fzf = FzfPrompt()
        options = ["Headless (background, faster)", "Visible (you can see the browser)"]
        choice = fzf.prompt(options, "--prompt='Select browser mode: '")
        
        if choice and "Visible" in choice[0]:
            headless = False
        else:
            headless = True  # Default to headless
    with NovaAct(
        starting_page="https://facebook.com",
        user_data_dir=user_data_dir,
        headless=headless,
        clone_user_data_dir=False,
    ) as nova:
        # Navigate to Marketplace
        nova.act("Click on Marketplace in the left sidebar or navigation menu.")
        nova.act(f'Search for "{search_item}".')
        
        # Click on sorting options
        # nova.act("Click on 'Trier par' to open sorting options.")
        
        # Filter for recent items (last 24 hours)
        # nova.act("Select the option to show most recent items first .")
        # Click on sale date
        nova.act("Click on 'date de mise en vente ' to open sale date.")
        
        # Filter for recent items (last 24 hours)
        nova.act("Select the option to show items  posted in the last 24 hours.")
 
        
        # Extract the first 5 items from search results
        result = nova.act(
            'Get the first 5 marketplace items from the search results. For each item, extract the title, price, location, and only the time portion from "Publié il y a" (for example: if you see "Publié il y a une semaine dans Montréal, QC", extract only "une semaine"). If no time is found, use "Date not specified".',
            schema=MarketplaceItems.model_json_schema()
        )
        
        if result.matches_schema:
            items = MarketplaceItems.model_validate(result.parsed_response)
            print("\nFirst 5 Facebook Marketplace items (filtered results):")
            print("-" * 60)
            for i, item in enumerate(items.items, 1):
                print(f"{i}. {item.title}")
                print(f"   Price: {item.price}")
                print(f"   Location: {item.location}")
                print(f"   Posted: {item.time_posted}")
                print()
        else:
            # Handle case where response format doesn't match schema exactly
            try:
                # Try to parse as MarketplaceItems object
                items = MarketplaceItems.model_validate(result.parsed_response)
                print("\nFirst 5 Facebook Marketplace items (filtered results):")
                print("-" * 60)
                for i, item in enumerate(items.items, 1):
                    print(f"{i}. {item.title}")
                    print(f"   Price: {item.price}")
                    print(f"   Location: {item.location}")
                    print(f"   Posted: {item.time_posted}")
                    print()
            except Exception:
                # Try to parse as list
                try:
                    if isinstance(result.parsed_response, list):
                        items_list = [MarketplaceItem.model_validate(item) for item in result.parsed_response]
                        print("\nFirst 5 Facebook Marketplace items (filtered results):")
                        print("-" * 60)
                        for i, item in enumerate(items_list, 1):
                            print(f"{i}. {item.title}")
                            print(f"   Price: {item.price}")
                            print(f"   Location: {item.location}")
                            print(f"   Posted: {item.time_posted}")
                            print()
                    else:
                        print(f"Failed to extract items: {result.response}")
                except Exception as e:
                    print(f"Error parsing response: {e}")
                    print(f"Raw response: {result.response}")
        
        if not headless:
            input("Press Enter to close the browser...")


if __name__ == "__main__":
    fire.Fire(main)
