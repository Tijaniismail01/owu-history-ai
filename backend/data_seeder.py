import os

def create_data():
    raw_data_path = "./data/raw"
    if not os.path.exists(raw_data_path):
        os.makedirs(raw_data_path)

    data = {
        "origins.txt": """
The Owu people are a subgroup of the Yoruba people of West Africa.
Owu history begins with their first settlement (Owu-Ipole) in the 14th century.
According to oral tradition, the first Olowu (King of Owu) was a prince of the Ife kingdom, son of Oduduwa's daughter.
The crown of Owu is said to have been brought from Ile-Ife by the first King, Pawu.
They are known for their strong warrior tradition and were the first Yoruba kingdom to organize a standing army.
""",
        "wars.txt": """
The Owu Kingdom was destroyed in the early 19th century (approx. 1821-1825) during the Owu Wars.
This war was a major catalyst for the Yoruba civil wars that followed.
The combined forces of Ife and Ijebu laid siege to Owu-Ipole for five years before it fell.
Following the destruction, the Owu people were dispersed across Yorubaland.
Many Owu refugees settled in Abeokuta, where they established the Owu quarter.
""",
        "culture.txt": """
Owu people are distinct in their facial marks (six incisions on each cheek).
They are known for the "Aro" festival which celebrates their heritage.
The Olowu of Owu is the paramount ruler.
Owu dialect is a unique variation of the Yoruba language.
They are praised as "Owu lakoda" meaning "Owu the first created".
"""
    }

    for filename, content in data.items():
        file_path = os.path.join(raw_data_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Created {file_path}")

if __name__ == "__main__":
    create_data()
