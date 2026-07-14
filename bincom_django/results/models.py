from django.db import models

# --------------------------------------------------------------------------
# These are UNMANAGED (managed=False) models mapped onto bincom_test.sql
# --------------------------------------------------------------------------


class State(models.Model):
    state_id = models.IntegerField(primary_key=True)
    state_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "states"

    def __str__(self):
        return self.state_name


class Lga(models.Model):
    uniqueid = models.AutoField(primary_key=True)
    lga_id = models.IntegerField()          # business id -- ward/polling_unit.lga_id joins on THIS
    lga_name = models.CharField(max_length=50)
    state_id = models.IntegerField()        # raw FK to states.state_id (no DB-level constraint exists)
    lga_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "lga"

    def __str__(self):
        return self.lga_name


class Ward(models.Model):
    uniqueid = models.AutoField(primary_key=True)
    ward_id = models.IntegerField()         # only unique WITHIN an lga
    ward_name = models.CharField(max_length=50)
    lga_id = models.IntegerField()          # joins to Lga.lga_id, NOT Lga.uniqueid
    ward_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ward"

    def __str__(self):
        return self.ward_name


class PollingUnit(models.Model):
    uniqueid = models.AutoField(primary_key=True)
    polling_unit_id = models.IntegerField()
    ward_id = models.IntegerField()         # per-LGA ward number, same scheme as Ward.ward_id
    lga_id = models.IntegerField()          # joins to Lga.lga_id
    uniquewardid = models.IntegerField(blank=True, null=True)  # clean join to Ward.uniqueid
    polling_unit_number = models.CharField(max_length=50, blank=True, null=True)
    polling_unit_name = models.CharField(max_length=50, blank=True, null=True)
    polling_unit_description = models.TextField(blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    long = models.CharField(max_length=255, blank=True, null=True)
    entered_by_user = models.CharField(max_length=50, blank=True, null=True)
    date_entered = models.CharField(max_length=50, blank=True, null=True)
    user_ip_address = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "polling_unit"

    def __str__(self):
        return self.polling_unit_name or f"PU {self.uniqueid}"


class Party(models.Model):
    id = models.AutoField(primary_key=True)
    partyid = models.CharField(max_length=11)     # abbreviation, e.g. 'PDP'
    partyname = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = "party"

    def __str__(self):
        return self.partyname


class AnnouncedPuResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    polling_unit_uniqueid = models.CharField(max_length=50)  # VARCHAR in the DB; compare as string
    party_abbreviation = models.CharField(max_length=4)
    party_score = models.IntegerField()
    entered_by_user = models.CharField(max_length=50, blank=True, null=True)
    date_entered = models.CharField(max_length=50, blank=True, null=True)
    user_ip_address = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "announced_pu_results"


class AnnouncedLgaResult(models.Model):
    """
    NOTE: `lga_name` actually stores the LGA's numeric lga_id as a string,
    not its text name. Q2 deliberately does not use this table -- it's
    kept here only in case when needed for cross-checking.
    """
    result_id = models.AutoField(primary_key=True)
    lga_name = models.CharField(max_length=50)
    party_abbreviation = models.CharField(max_length=4)
    party_score = models.IntegerField()
    entered_by_user = models.CharField(max_length=50, blank=True, null=True)
    date_entered = models.CharField(max_length=50, blank=True, null=True)
    user_ip_address = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "announced_lga_results"
