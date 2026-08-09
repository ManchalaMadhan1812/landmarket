"""
Elasticsearch document definitions for property search
"""

from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from apps.properties.models import Property

# Define the index
properties_index = Index('properties')
properties_index.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        'analyzer': {
            'default': {
                'type': 'standard',
                'stopwords': '_english_'
            },
            'autocomplete': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': ['lowercase', 'stop', 'asciifolding']
            }
        },
        'tokenizer': {
            'autocomplete': {
                'type': 'edge_ngram',
                'min_gram': 2,
                'max_gram': 20,
                'token_chars': ['letter', 'digit', 'whitespace']
            }
        }
    }
)


@registry.register_document
class PropertyDocument(Document):
    """
    Elasticsearch document for Property model with geolocation support
    """
    # Text fields
    id = fields.KeywordField()
    title = fields.TextField(
        analyzer='standard',
        fields={'autocomplete': fields.TextField(analyzer='autocomplete')}
    )
    description = fields.TextField(analyzer='standard')
    address = fields.TextField(analyzer='standard')
    
    # Keyword fields for filtering
    property_type = fields.KeywordField()
    purpose = fields.KeywordField()
    status = fields.KeywordField()
    city = fields.KeywordField()
    state = fields.KeywordField()
    district = fields.KeywordField()
    pincode = fields.KeywordField()
    
    # Numeric fields
    price = fields.IntegerField()
    total_area = fields.FloatField()
    area_unit = fields.KeywordField()
    view_count = fields.IntegerField()
    save_count = fields.IntegerField()
    verification_score = fields.IntegerField()
    
    # Location field (geo-point for distance queries)
    location = fields.GeoPointField()
    
    # Owner information
    owner_id = fields.KeywordField()
    owner_name = fields.TextField()
    owner_email = fields.KeywordField()
    
    # Broker information
    broker_id = fields.KeywordField()
    broker_name = fields.TextField()
    
    # Amenities and features (nested for complex queries)
    amenities = fields.TextField()
    features = fields.TextField()
    
    # Survey and land records
    survey_number = fields.KeywordField()
    patta_number = fields.KeywordField()
    chitta_number = fields.KeywordField()
    rera_number = fields.KeywordField()
    
    # Dates for sorting
    created_at = fields.DateField()
    updated_at = fields.DateField()
    
    # Nested reviews for aggregation
    avg_rating = fields.FloatField()
    review_count = fields.IntegerField()
    
    class Index:
        name = 'properties'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'property_type',
            'purpose',
            'price',
            'total_area',
            'area_unit',
            'address',
            'city',
            'state',
            'district',
            'pincode',
            'status',
            'view_count',
            'save_count',
            'verification_score',
            'created_at',
            'updated_at',
        ]

        # Signals that trigger indexing
        related_models = []

    def prepare_location(self, instance):
        """Convert PostGIS point to geo-point format for Elasticsearch"""
        if instance.location:
            return {
                'lat': instance.location.y,
                'lon': instance.location.x,
            }
        return None

    def prepare_owner_name(self, instance):
        """Prepare owner full name"""
        return instance.owner.get_full_name()

    def prepare_owner_email(self, instance):
        """Prepare owner email"""
        return instance.owner.email

    def prepare_broker_name(self, instance):
        """Prepare broker name if exists"""
        if instance.broker:
            return instance.broker.get_full_name()
        return None

    def prepare_broker_id(self, instance):
        """Prepare broker ID if exists"""
        if instance.broker:
            return str(instance.broker.id)
        return None

    def prepare_amenities(self, instance):
        """Convert amenities dict to searchable text"""
        if instance.amenities:
            return ' '.join(instance.amenities.keys())
        return ''

    def prepare_features(self, instance):
        """Convert features dict to searchable text"""
        if instance.features:
            return str(instance.features)
        return ''

    def prepare_avg_rating(self, instance):
        """Calculate average rating from reviews"""
        reviews = instance.reviews.all()
        if reviews:
            total_rating = sum(r.rating for r in reviews)
            return total_rating / len(reviews)
        return 0.0

    def prepare_review_count(self, instance):
        """Get count of reviews"""
        return instance.reviews.count()