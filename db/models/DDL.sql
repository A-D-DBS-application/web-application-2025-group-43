
CREATE TABLE public.garden (
  garden_id uuid NOT NULL DEFAULT gen_random_uuid(),
  garden_name text NOT NULL,
  adress_garden text,
  area_garden numeric,
  user_email text,
  CONSTRAINT garden_pkey PRIMARY KEY (garden_id),
  CONSTRAINT garden_user_email_fkey FOREIGN KEY (user_email) REFERENCES public.user(uemail)
);
CREATE TABLE public.health_score (
  hid bigint NOT NULL DEFAULT nextval('health_score_hid_seq'::regclass),
  score double precision NOT NULL,
  calculated_at timestamp with time zone NOT NULL,
  serial_number character varying NOT NULL,
  score_date date,
  CONSTRAINT health_score_pkey PRIMARY KEY (hid),
  CONSTRAINT health_score_serial_number_fkey FOREIGN KEY (serial_number) REFERENCES public.robot_zone(serial_number)
);
CREATE TABLE public.measurement (
  mid bigint NOT NULL DEFAULT nextval('measurement_mid_seq'::regclass),
  value numeric NOT NULL,
  time_m timestamp with time zone NOT NULL DEFAULT now(),
  srnr_sensor text NOT NULL,
  CONSTRAINT measurement_pkey PRIMARY KEY (mid),
  CONSTRAINT measurement_srnr_sensor_fkey FOREIGN KEY (srnr_sensor) REFERENCES public.sensor(srnr_sensor)
);
CREATE TABLE public.plant_profiles (
  plant_name text NOT NULL UNIQUE,
  display_name text NOT NULL,
  temperature_mean numeric,
  temperature_std numeric,
  soil_moisture_mean numeric,
  soil_moisture_std numeric,
  humidity_mean numeric,
  humidity_std numeric,
  rain_mm_week_mean numeric,
  rain_mm_week_std numeric,
  ppfd_mean numeric,
  ppfd_std numeric,
  co2_mean numeric,
  co2_std numeric,
  CONSTRAINT plant_profiles_pkey PRIMARY KEY (plant_name)
);
CREATE TABLE public.robot_zone (
  serial_number text NOT NULL,
  area_playfield numeric,
  robot_name text,
  garden_id uuid,
  plant_name text,
  CONSTRAINT robot_zone_pkey PRIMARY KEY (serial_number),
  CONSTRAINT robot_zone_garden_id_fkey FOREIGN KEY (garden_id) REFERENCES public.garden(garden_id),
  CONSTRAINT robot_zone_plant_profile_plant_name_fkey FOREIGN KEY (plant_name) REFERENCES public.plant_profiles(plant_name)
);
CREATE TABLE public.sensor (
  srnr_sensor text NOT NULL,
  sensor_type text NOT NULL CHECK (sensor_type = ANY (ARRAY['temperature'::text, 'humidity'::text, 'co2'::text, 'moisture'::text, 'rain'::text, 'light'::text])),
  unit text,
  serial_number text NOT NULL,
  CONSTRAINT sensor_pkey PRIMARY KEY (srnr_sensor),
  CONSTRAINT sensor_serial_number_fkey FOREIGN KEY (serial_number) REFERENCES public.robot_zone(serial_number)
);
CREATE TABLE public.user (
  uemail text NOT NULL,
  uname text NOT NULL,
  phone text,
  adress text,
  CONSTRAINT user_pkey PRIMARY KEY (uemail)
);