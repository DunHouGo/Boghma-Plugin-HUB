CONTAINER pypreference
{
	NAME pypreference;

	GROUP
	{
		SEPARATOR BOGHMA_PYPREFERENCE_MAIN_GROUP { }
		GROUP
		{

		DEFAULT 1;
		BOOL BOGHMA_PYPREFERENCE_SHOW_IN_TOPMENU { ANIM OFF; }
  
		}

		

		GROUP
		{
		DEFAULT 1;
		COLUMNS 2;

		STRING BOGHMA_PYPREFERENCE_ASSET_FOLDER { SCALE_H; } 

		//BUTTON BOGHMA_PYPREFERENCE_BUTTON { ALIGN_RIGHT; }

        BITMAPBUTTON BOGHMA_PYPREFERENCE_BUTTON
        {
            SIZE 20;
            BUTTON;
            ICONID1 1027025;
        }
		}
	}
}
