from django.db import models
import uuid

class Intersection(models.Model):
    location = models.PointField()
    name = models.CharField(max_length=100)

class Sensor(models.Model):
    mounting_height = models.DecimalField(max_digits=5, decimal_places=2)
    rotate_x = models.DecimalField(max_digits=5, decimal_places=2)
    rotate_y = models.DecimalField(max_digits=5, decimal_places=2)
    rotate_z = models.DecimalField(max_digits=5, decimal_places=2)
    x_coordinate = models.DecimalField(max_digits=10, decimal_places=2)
    y_coordinate = models.DecimalField(max_digits=10, decimal_places=2)
    sensor_type = models.CharField(max_length=50)
    sensor_ip = models.GenericIPAddressField()
    port = models.IntegerField()
    command_port = models.IntegerField()
    firmware_version = models.CharField(max_length=50)
    intersection = models.ForeignKey(Intersection, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Lane(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    center = models.DecimalField(max_digits=10, decimal_places=2)
    direction = models.IntegerField()
    width = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField()
    intersection = models.ForeignKey(Intersection, on_delete=models.CASCADE)

class DetectionZone(models.Model):
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    classes = models.IntegerField()
    zone_offset = models.DecimalField(max_digits=10, decimal_places=2)

class VehicleDetection(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    obj_id = models.IntegerField()
    speed_mps = models.DecimalField(max_digits=10, decimal_places=2)
    detection_time = models.DateTimeField()
    point_x = models.DecimalField(max_digits=10, decimal_places=2)
    point_y = models.DecimalField(max_digits=10, decimal_places=2)

class TrafficQueue(models.Model):
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    max_length = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    growth_rate = models.DecimalField(max_digits=10, decimal_places=4)

class TrafficLight(models.Model):
    intersection = models.ForeignKey(Intersection, on_delete=models.CASCADE)
    current_phase = models.CharField(max_length=20)
    phase_duration = models.IntegerField()

