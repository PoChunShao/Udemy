from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic",cascade="all,delete")
    """
    lazy => https://shomy.top/2016/08/11/flask-sqlalchemy-relation-lazy/
    back_populates => https://www.cnblogs.com/kirito-c/p/10900024.html
    cascade => 同上連結，(all,delete)表示當刪除商店模型（StoreModel）時，
    相關聯的所有商品模型（ItemModel）也會被刪除，確保數據的一致性和完整性
    """