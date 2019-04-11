from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, CategoryItem
 
# Connect to database
engine = create_engine('sqlite:///recreationalwarehouse.db')
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


#List for Soccer
category1 = Category(name = "Soccer")

session.add(category1)
session.commit()


categoryItem1 = CategoryItem(name = "Boots", description = "Genuine leather balanced to fit any foot. Light and sturdy allowing for fast footwork and durability for power kicks.", category = category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = "Ball", description = "Hand stiched ball made of genuine leather.", category = category1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name = "Shin guards", description = "Durable plastic to endure kicks to the shins, lightweight.", category = category1)

session.add(categoryItem3)
session.commit()


#List for Football
category2 = Category(name = "Football")

session.add(category2)
session.commit()


categoryItem1 = CategoryItem(name = "Helmet", description = "A must have. Protect the money maker and your mental state.", category = category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = "Shoulder pads", description = "Pads that not only are useful to break tackles but look intimidating.", category = category2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name = "Gloves", description = "Great for gripping balls and grabbing jerseys.", category = category2)

session.add(categoryItem3)
session.commit()


#List for Tennis
category3 = Category(name = "Tennis")

session.add(category3)
session.commit()


categoryItem1 = CategoryItem(name = "Racket", description = "Carbon fiber, lightweight, ready for agressive swings. Ergonomic, built to avoid tennis elbow.", category = category3)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = "Headband", description = "Tight, not too tight, piece of cloth to absorb all potential distracting sweat drops from going in your eyes.", category = category3)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name = "Shoes", description = "Super lightweight, barefoot feel. For maximum speed potentional without sacrificing ankle support for those life changing pivots.", category = category3)

session.add(categoryItem3)
session.commit()


#List for Basketball
category4 = Category(name = "Basketball")

session.add(category4)
session.commit()


categoryItem1 = CategoryItem(name = "Shoes", description = "Great ankle support. Includes a nifty feature, pump button on the tounge of shoe and creates cloud-like walking experience.", category = category4)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = "Ball", description = "Made from genuine pig skin. Grip capabilities increased with innovative technology.", category = category4)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name = "Warm-up gear", description = "Whole outfit, jacket and pants, to help get you warm before a game. Also adds style points when warming the bench.", category = category4)

session.add(categoryItem3)
session.commit()


#List for Hockey
category5 = Category(name = "Hockey")

session.add(category5)
session.commit()


categoryItem1 = CategoryItem(name = "Hockey stick", description = "Made from the sturdiest hardwood that exists. Not the lightest peice of equipment but, arguably the most effective.", category = category5)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = "Puck", description = "Made from the coal smuggled from Santa\'s workshop. Contains mystical abilities even goalies can't grasp.", category = category5)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name = "Skates", description = "A must have. Comes in either style, roller or blade.", category = category5)

session.add(categoryItem3)
session.commit()


print "added rec items!"